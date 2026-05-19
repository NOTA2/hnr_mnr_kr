# ROM Text Extraction Gap Audit

- ROM: `/Users/user/test/Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba`
- extracted interval count: `23021`
- missing-candidate count: `21583`
- high-confidence count: `0`
- suppressed high-confidence false positives: `2`

## High Confidence Candidates

These still need human review. The score only means the bytes look more like real UI/script text than code or compressed data.


## Suppressed High Confidence False Positives

These byte runs were manually classified as broad-scan noise and are suppressed so new real gaps stand out.

- score=`7` `0x2A3B3C` `7` bytes term=`0x00` jp=`0.4` reasons=`00-terminated,jp>=2,kana>=2,len>=5`: 033ムヨ (CP932 broad-scan false positive; no stable UI/text context.)
- score=`6` `0x52A4E4` `7` bytes term=`0x00` jp=`0.4` reasons=`00-terminated,jp>=2,kana>=2,len>=5,halfwidth-kana-penalty`: KずﾛBず (CP932 broad-scan false positive/noise.)

## Broad Candidates

This broad list is intentionally noisy and is mainly useful for scripted follow-up filters.

- `0x000049` `7` bytes term=`None` jp=`0.4`: ﾊ啾X離'
- `0x000219` `7` bytes term=`None` jp=`0.4`: ﾊ啾X離'
- `0x000DDC` `7` bytes term=`None` jp=`0.4`: 牲魂oF8
- `0x004448` `6` bytes term=`0x00` jp=`0.5`: 牲げoF
- `0x00461F` `7` bytes term=`0x00` jp=`0.4`: G牲げoF
- `0x005E18` `6` bytes term=`0x00` jp=`0.5`: 鴾q熕/
- `0x005E94` `6` bytes term=`0x00` jp=`0.5`: 入0熕/
- `0x0064F4` `7` bytes term=`None` jp=`0.4`: 牲げoF9
- `0x006D14` `7` bytes term=`None` jp=`0.4`: 牲顕oF9
- `0x009764` `7` bytes term=`None` jp=`0.4`: 牲顕oF8
- `0x009C80` `6` bytes term=`0x00` jp=`0.5`: ｵ鄕牴)
- `0x009EF4` `6` bytes term=`0x00` jp=`0.5`: {惞狢)
- `0x009F78` `6` bytes term=`0x00` jp=`0.5`: 9僘熕/
- `0x00A58F` `7` bytes term=`None` jp=`0.4`: ﾑﾖ瑪澡H
- `0x00AC5F` `7` bytes term=`0x00` jp=`0.4`: ﾝﾓ澹犧(
- `0x00BA70` `6` bytes term=`0x00` jp=`0.5`: ]鏞筅)
- `0x00BF10` `6` bytes term=`0x00` jp=`0.5`: m咩燿*
- `0x00C309` `11` bytes term=`None` jp=`0.571`: p姨姜價有#x
- `0x00C33D` `9` bytes term=`None` jp=`0.5`: x終繰記#x
- `0x00CB10` `6` bytes term=`0x00` jp=`0.5`: ﾉ絈濮)
- `0x00D9A9` `6` bytes term=`None` jp=`0.5`: !沆ｿ瀇
- `0x00DA05` `6` bytes term=`None` jp=`0.5`: !沆蛸!
- `0x011E26` `10` bytes term=`None` jp=`0.429`: 戛昶8h9h撹
- `0x012E94` `7` bytes term=`None` jp=`0.4`: 牲峅oF9
- `0x016980` `6` bytes term=`0x00` jp=`0.5`: 只5笄*
- `0x016CFC` `6` bytes term=`0x00` jp=`0.5`: w劯燿*
- `0x017D14` `6` bytes term=`None` jp=`0.5`: 牲鴫oF
- `0x017ED8` `7` bytes term=`None` jp=`0.4`: 顆p汯`<
- `0x018A68` `7` bytes term=`None` jp=`0.4`: 丨ﾓ芋$$
- `0x01A2A0` `6` bytes term=`None` jp=`0.5`: 沆B琪H
- `0x01A2BA` `6` bytes term=`None` jp=`0.5`: 沆5珖H
- `0x01A2D4` `6` bytes term=`None` jp=`0.5`: 沆(犱H
- `0x01A356` `6` bytes term=`None` jp=`0.5`: 沆鋺;H
- `0x01AB09` `7` bytes term=`None` jp=`0.4`: !褶咨ｯI
- `0x01AB13` `7` bytes term=`None` jp=`0.4`: !褶美ｭI
- `0x01AB1D` `7` bytes term=`None` jp=`0.4`: !褶飾ｬI
- `0x01B70D` `9` bytes term=`None` jp=`0.5`: (%ﾐ僮僣露
- `0x01BF7F` `6` bytes term=`None` jp=`0.5`: #蔔傅!
- `0x01BFA2` `6` bytes term=`None` jp=`0.5`: 蔔聯9h
- `0x01C1C7` `7` bytes term=`0x00` jp=`0.4`: G牲顕oF
- `0x01C758` `6` bytes term=`0x00` jp=`0.5`: 牲顕oF
- `0x01CC68` `7` bytes term=`None` jp=`0.4`: 胱ｨ砡`8
- `0x01CE06` `7` bytes term=`None` jp=`0.4`: 胱ﾙ偆`8
- `0x01CE5E` `7` bytes term=`None` jp=`0.4`: 胱ｭ偆`8
- `0x01CEA2` `7` bytes term=`None` jp=`0.4`: 胱釧x`8
- `0x01CEE6` `7` bytes term=`None` jp=`0.4`: 胱i偆`8
- `0x01CF2A` `7` bytes term=`None` jp=`0.4`: 胱G偆`8
- `0x01CF6E` `7` bytes term=`None` jp=`0.4`: 胱%偆`8
- `0x01CFF6` `7` bytes term=`None` jp=`0.4`: 胱碼x`8
- `0x01DCDC` `7` bytes term=`None` jp=`0.4`: 糯n砡`8
- `0x01F50C` `7` bytes term=`None` jp=`0.4`: 沆ｸ鄕hA
- `0x01F67C` `7` bytes term=`None` jp=`0.4`: 沆ｮ汯hA
- `0x01FB93` `6` bytes term=`None` jp=`0.5`: "顆ﾊ鍈
- `0x01FBFF` `6` bytes term=`None` jp=`0.5`: "顆琵(
- `0x01FC57` `6` bytes term=`None` jp=`0.5`:  顆V髙
- `0x01FDED` `8` bytes term=`None` jp=`0.6`: "顆暹1澑
- `0x0216C9` `7` bytes term=`None` jp=`0.4`: h沆錮9h
- `0x021AB9` `9` bytes term=`0x00` jp=`0.5`: "踟7硤猜5
- `0x02559E` `6` bytes term=`None` jp=`0.5`: 奬瀏9h
- `0x026AE2` `7` bytes term=`None` jp=`0.4`: 8h沆檄9
- `0x0275F7` `7` bytes term=`None` jp=`0.4`: ($ﾐ顆戒
- `0x02940D` `6` bytes term=`0xFF` jp=`0.5`: 堂#鴒H
- `0x029B72` `7` bytes term=`None` jp=`0.75`: 鴒練[瀾
- `0x02A40C` `7` bytes term=`None` jp=`0.4`: 牲げoF9
- `0x02A760` `7` bytes term=`None` jp=`0.4`: 牲峅oF8
- `0x02AA30` `7` bytes term=`None` jp=`0.4`: ｡ 鴒5錝
- `0x02AA45` `7` bytes term=`None` jp=`0.4`: ｵoF顆戍
- `0x02AE7B` `7` bytes term=`None` jp=`0.4`: j針ﾐb礎
- `0x02AEB1` `9` bytes term=`None` jp=`0.5`: "色礑詮fF
- `0x02C009` `7` bytes term=`None` jp=`0.4`: ずh9i岳
- `0x02C0C3` `7` bytes term=`None` jp=`0.4`: Bn炬j丨
- `0x02C0DF` `7` bytes term=`None` jp=`0.4`: B`炬j丨
- `0x02C567` `7` bytes term=`None` jp=`0.4`: ずh9i岳
- `0x02C621` `7` bytes term=`None` jp=`0.4`: B9炬j丨
- `0x02C63F` `7` bytes term=`None` jp=`0.4`: 炬jyh琪
- `0x02C65D` `6` bytes term=`None` jp=`0.5`: 璧h仼Q
- `0x02D27D` `7` bytes term=`None` jp=`0.4`: ボ犧hｹh
- `0x02D2DB` `7` bytes term=`None` jp=`0.4`: キ犧hｹh
- `0x02E9E5` `7` bytes term=`None` jp=`0.4`: FEF犇恐
- `0x02EA18` `7` bytes term=`None` jp=`0.4`: ｽた皆F5
- `0x02EC22` `7` bytes term=`None` jp=`0.4`: ｾだ界F.
- `0x02F0A6` `7` bytes term=`None` jp=`0.4`: 引(`筆8
- `0x02F0C4` `8` bytes term=`None` jp=`0.6`: (`舟紀秋
- `0x02F0D2` `8` bytes term=`None` jp=`0.6`: (`庚蟹稀
- `0x02F329` `7` bytes term=`None` jp=`0.4`: FEF犇顕
- `0x0308B4` `7` bytes term=`None` jp=`0.4`: 漲濮xh9
- `0x032BAF` `7` bytes term=`None` jp=`0.4`: ずi9j岳
- `0x032C25` `7` bytes term=`None` jp=`0.4`: Bﾙ炬j仡
- `0x032C43` `7` bytes term=`None` jp=`0.4`: 炬jyl琩
- `0x033488` `7` bytes term=`None` jp=`0.4`: 牲げoF8
- `0x033866` `6` bytes term=`None` jp=`0.5`: 毘y炸h
- `0x033870` `6` bytes term=`None` jp=`0.5`: 碼t炸h
- `0x03387A` `6` bytes term=`None` jp=`0.5`: 厚o炸h
- `0x033884` `6` bytes term=`None` jp=`0.5`: ﾛ仼炸h
- `0x03388E` `6` bytes term=`None` jp=`0.5`: 棋e炸h
- `0x033898` `6` bytes term=`None` jp=`0.5`: 滌`炸h
- `0x03594C` `6` bytes term=`None` jp=`0.5`: 牲げoF
- `0x03C3AB` `7` bytes term=`None` jp=`0.4`: ﾑｼ癨糲l
- `0x03DCA5` `7` bytes term=`None` jp=`0.4`: j伃瑢}k
- `0x03DD53` `7` bytes term=`None` jp=`0.4`: j伃瑢}k
- `0x045553` `9` bytes term=`None` jp=`0.8`: 燎叨?囮劔
- `0x046C97` `6` bytes term=`None` jp=`0.5`: ﾑｾ狒狎
- `0x0477D6` `6` bytes term=`None` jp=`0.5`: k瀋犹h
- `0x0492BB` `7` bytes term=`None` jp=`0.4`: ﾑS筺篋h
- `0x049763` `6` bytes term=`None` jp=`0.5`: 蹲犧hﾂ
- `0x04A1CF` `7` bytes term=`None` jp=`0.4`: G牲げoF
- `0x04A860` `8` bytes term=`None` jp=`0.6`: 改ｺ犹炸h
- `0x04AA44` `6` bytes term=`None` jp=`0.5`: 練h犹h
- `0x04AA6D` `7` bytes term=`None` jp=`0.75`: 焄澳犹h
- `0x04ABAC` `8` bytes term=`None` jp=`0.6`: 脣T澳犹h
- `0x04ACC4` `6` bytes term=`None` jp=`0.5`: W丨犹h
- `0x04ACEC` `8` bytes term=`None` jp=`0.4`: C￢澳犹h
- `0x04AE40` `8` bytes term=`None` jp=`0.6`: 咬`濱犹h
- `0x04AFB0` `8` bytes term=`None` jp=`0.6`: 碾^濔犹h
- `0x04BE58` `7` bytes term=`None` jp=`0.4`: 煆,汯`8
- `0x04C77C` `6` bytes term=`None` jp=`0.5`: ｪ罠絆I
- `0x04FB7E` `8` bytes term=`0x00` jp=`0.6`: 蹂鴒糺:I
- `0x04FE7A` `7` bytes term=`None` jp=`0.4`: 鴒e奓!ﾉ
- `0x050AF7` `6` bytes term=`None` jp=`0.5`: "踟2閒
- `0x050D56` `6` bytes term=`None` jp=`0.5`: 蔔e匇H
- ... `21463` more candidates omitted from markdown preview.
