#!/usr/bin/env swift

import AppKit
import Foundation

struct ToolError: Error, CustomStringConvertible {
    let message: String
    var description: String { message }
}

struct Config {
    var fontName: String
    var manifestPath: String
    var outputDir: String
    var fontSize: Double = 11.0
    var canvasWidth: Int = 12
    var canvasHeight: Int = 12
    var baselineAdjust: Double = -1.0
    var xOffset: Double = 0.0
    var yOffset: Double = 0.0
    var reportPath: String?
}

func parseArgs(_ args: [String]) throws -> Config {
    var values: [String: String] = [:]
    var index = 1
    while index < args.count {
        let key = args[index]
        guard key.hasPrefix("--") else {
            throw ToolError(message: "지원하지 않는 인자: \(key)")
        }
        guard index + 1 < args.count else {
            throw ToolError(message: "값이 없는 인자: \(key)")
        }
        values[key] = args[index + 1]
        index += 2
    }

    guard let fontName = values["--font-name"] else {
        throw ToolError(message: "--font-name 이 필요합니다.")
    }
    guard let manifestPath = values["--manifest"] else {
        throw ToolError(message: "--manifest 가 필요합니다.")
    }
    guard let outputDir = values["--output-dir"] else {
        throw ToolError(message: "--output-dir 이 필요합니다.")
    }

    var config = Config(fontName: fontName, manifestPath: manifestPath, outputDir: outputDir)
    if let raw = values["--font-size"], let value = Double(raw) { config.fontSize = value }
    if let raw = values["--canvas-width"], let value = Int(raw) { config.canvasWidth = value }
    if let raw = values["--canvas-height"], let value = Int(raw) { config.canvasHeight = value }
    if let raw = values["--baseline-adjust"], let value = Double(raw) { config.baselineAdjust = value }
    if let raw = values["--x-offset"], let value = Double(raw) { config.xOffset = value }
    if let raw = values["--y-offset"], let value = Double(raw) { config.yOffset = value }
    config.reportPath = values["--report"]
    return config
}

func loadManifest(path: String) throws -> [[String: Any]] {
    let data = try Data(contentsOf: URL(fileURLWithPath: path))
    let object = try JSONSerialization.jsonObject(with: data, options: [])
    guard let list = object as? [[String: Any]] else {
        throw ToolError(message: "manifest 는 JSON 배열이어야 합니다.")
    }
    return list
}

func sanitizeStem(_ value: String) -> String {
    let pattern = "[^0-9A-Za-z_.-]+"
    let stem = value.replacingOccurrences(of: pattern, with: "_", options: .regularExpression)
    return stem.trimmingCharacters(in: CharacterSet(charactersIn: "_"))
}

func renderGlyph(char: String, font: NSFont, width: Int, height: Int, baselineAdjust: Double, xOffset: Double, yOffset: Double) throws -> [UInt8] {
    guard let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: width,
        pixelsHigh: height,
        bitsPerSample: 8,
        samplesPerPixel: 1,
        hasAlpha: false,
        isPlanar: false,
        colorSpaceName: .deviceWhite,
        bitmapFormat: [],
        bytesPerRow: width,
        bitsPerPixel: 8
    ) else {
        throw ToolError(message: "bitmap surface 생성 실패")
    }

    guard let context = NSGraphicsContext(bitmapImageRep: rep) else {
        throw ToolError(message: "graphics context 생성 실패")
    }

    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = context
    defer { NSGraphicsContext.restoreGraphicsState() }

    NSColor.black.setFill()
    NSBezierPath(rect: NSRect(x: 0, y: 0, width: width, height: height)).fill()

    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = .center
    let attrs: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: NSColor.white,
        .paragraphStyle: paragraph,
    ]
    let nsString = NSString(string: char)
    let size = nsString.size(withAttributes: attrs)
    let drawRect = NSRect(
        x: floor((Double(width) - size.width) / 2.0 + xOffset),
        y: floor((Double(height) - size.height) / 2.0 + baselineAdjust + yOffset),
        width: ceil(size.width),
        height: ceil(size.height)
    )
    nsString.draw(in: drawRect, withAttributes: attrs)
    context.flushGraphics()

    guard let raw = rep.bitmapData else {
        throw ToolError(message: "bitmap data 접근 실패")
    }
    return Array(UnsafeBufferPointer(start: raw, count: width * height))
}

func writePGM(path: String, pixels: [UInt8], width: Int, height: Int) throws {
    var data = Data("P5\n\(width) \(height)\n255\n".utf8)
    data.append(contentsOf: pixels)
    FileManager.default.createFile(atPath: path, contents: data)
}

func writeJSON(path: String, object: Any) throws {
    let data = try JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .withoutEscapingSlashes])
    try data.write(to: URL(fileURLWithPath: path))
}

let args = CommandLine.arguments

if args.contains("--help") || args.count == 1 {
    let help = """
    usage:
      swift scripts/render_reference_font_workbench.swift \\
        --font-name 'Apple SD Gothic Neo' \\
        --manifest analysis/startup_intro_missing_manifest.json \\
        --output-dir /tmp/startup_font_seed

    optional:
      --font-size 11
      --canvas-width 12
      --canvas-height 12
      --baseline-adjust -1
      --x-offset 0
      --y-offset 0
      --report /path/to/report.json
    """
    print(help)
    exit(0)
}

do {
    let config = try parseArgs(args)
    let manifest = try loadManifest(path: config.manifestPath)
    let outputDirURL = URL(fileURLWithPath: config.outputDir, isDirectory: true)
    try FileManager.default.createDirectory(at: outputDirURL, withIntermediateDirectories: true)

    guard let font = NSFont(name: config.fontName, size: config.fontSize) else {
        throw ToolError(message: "폰트를 찾지 못했습니다: \(config.fontName)")
    }

    var preparedManifest: [[String: Any]] = []
    var reportEntries: [[String: Any]] = []
    var tableLines: [String] = []

    for (index, item) in manifest.enumerated() {
        guard let code = item["code"] as? String else {
            throw ToolError(message: "manifest 항목 \(index)에 code 가 없습니다.")
        }
        guard let char = item["char"] as? String, !char.isEmpty else {
            throw ToolError(message: "manifest 항목 \(index)에 char 가 없습니다.")
        }
        let stemSource = (item["name"] as? String) ?? (item["label"] as? String) ?? "glyph_\(code)"
        let stem = sanitizeStem(stemSource).isEmpty ? "glyph_\(code)" : sanitizeStem(stemSource)
        let pgmPath = outputDirURL.appendingPathComponent("\(stem).pgm").path

        let pixels = try renderGlyph(
            char: char,
            font: font,
            width: config.canvasWidth,
            height: config.canvasHeight,
            baselineAdjust: config.baselineAdjust,
            xOffset: config.xOffset,
            yOffset: config.yOffset
        )
        let nonzero = pixels.reduce(0) { $0 + ($1 == 0 ? 0 : 1) }
        try writePGM(path: pgmPath, pixels: pixels, width: config.canvasWidth, height: config.canvasHeight)

        preparedManifest.append([
            "code": code,
            "char": char,
            "pgm": pgmPath,
        ])
        tableLines.append("\(code.replacingOccurrences(of: "0x", with: "").uppercased())=\(char)")
        reportEntries.append([
            "index": index,
            "code": code,
            "char": char,
            "pgm": pgmPath,
            "nonzero_pixels": nonzero,
        ])
    }

    let preparedManifestPath = outputDirURL.appendingPathComponent("prepared_manifest.json").path
    let preparedTablePath = outputDirURL.appendingPathComponent("prepared.tbl").path
    try writeJSON(path: preparedManifestPath, object: preparedManifest)
    try Data(tableLines.joined(separator: "\n").appending("\n").utf8).write(to: URL(fileURLWithPath: preparedTablePath))

    let result: [String: Any] = [
        "font_name": config.fontName,
        "font_size": config.fontSize,
        "canvas_width": config.canvasWidth,
        "canvas_height": config.canvasHeight,
        "baseline_adjust": config.baselineAdjust,
        "x_offset": config.xOffset,
        "y_offset": config.yOffset,
        "manifest": config.manifestPath,
        "output_dir": config.outputDir,
        "prepared_manifest": preparedManifestPath,
        "prepared_table": preparedTablePath,
        "count": reportEntries.count,
        "entries": reportEntries,
    ]
    if let reportPath = config.reportPath {
        try writeJSON(path: reportPath, object: result)
    }

    print("font            : \(config.fontName)")
    print("prepared_dir    : \(config.outputDir)")
    print("prepared_count  : \(reportEntries.count)")
    print("prepared_manifest: \(preparedManifestPath)")
    print("table           : \(preparedTablePath)")
    if let reportPath = config.reportPath {
        print("report          : \(reportPath)")
    }
} catch {
    fputs("error: \(error)\n", stderr)
    exit(1)
}
