
import re
from collections import namedtuple


class ProhibitationPropertySet:
    OTHERS          = 0
    SEPARATION      = 1
    NOT_START       = 2
    NOT_END         = 3
    NOT_SEPARATION  = 4

    pattern = {
        SEPARATION: [
            r'[\s\r\n]'
        ],
        NOT_START: [
            r'[,.\])}]',
            r'[、。，．・：；）｝〕〉》」』】〙〗〟’”｠»]'
        ],
        NOT_END: [
            r'[\[({]',
            r'[（｛〔〈《「『【〘〖〝‘“｟«]'
        ]
    }

    inseparable = [
        (OTHERS,            NOT_START       ),
        (SEPARATION,        NOT_START       ),
        (NOT_START,         NOT_START       ),
        (NOT_END,           NOT_START       ),
        (NOT_SEPARATION,    NOT_START       ),
        (NOT_END,           OTHERS          ),
        (NOT_END,           SEPARATION      ),
        (NOT_END,           NOT_START       ),
        (NOT_END,           NOT_END         ),
        (NOT_END,           NOT_SEPARATION  ),
    ]

    separable = [
        (SEPARATION,        SEPARATION      ),
        (SEPARATION,        OTHERS          ),
        (SEPARATION,        NOT_END         ),
        (OTHERS,            SEPARATION      ),
        (NOT_START,         SEPARATION      ),
    ]

class CharacterPropertySet:
    UNKNOWN         = 0
    LATIN           = 1
    CJK             = 2
    HANGLE          = 3
    THAI_V          = 4
    THAI_C          = 5
    SYMBOL          = 6

    pattern = {
        SYMBOL: [
            r'[\u2000-\u206F]'                  # General Punctuation
        ],
        LATIN:  [
            r'[\u0000-\u007F]',                 # Basic Latain
            r'[\u0080-\u00FF]',                 # Latain-1 Supplement
            r'[\u0100-\u017F\u0180-\u024F]',    # Latain Extended-A, Latain Extended-B
            r'[\u2C60-\u2C7F]',                 # Latain Extended-C
            r'[\uA720-\uA7FF\uAB30-\uAB6F]',    # Latain Extended-D, Latain Extended-E
            r'[\u0400-\u04FF\u0500-\u052F]',    # Cyrillic, Cyrillic Supplement
            r'[\u1E00-\u1EFF]',                 # Latin Extended Additional
            r'[\u2100-\u214F]'                  # Letterlike Symbols
        ],
        CJK:    [
            r'[\u3000-\u303F]',                 # CJK Symbols and Punctuation
            r'[\u3041-\u309F\u30A1-\u30FF]',    # Hiragana, Katakana
            r'[\u4E00-\u9FFF]',                 # CJK Unified Ideographs
            r'[\uFF00-\uFFEF]'                  # Halfwidth and Fullwidth Forms
        ],
        HANGLE: [
            r'[\uAC00-\uD7AF]'                  # Hangul Syllables
        ],
        THAI_V:  [
            r'[\u0E31\u0E33-\u0E3A\u0E47-\u0E4E]',  # Thai (Vowels)
        ],
        THAI_C:  [
            r'[\u0E00-\u0E7F]',                 # Thai (Consonant)
        ]
    }
    
    inseparable = [
        (LATIN,     LATIN   ),
        (HANGLE,    HANGLE  ),
        (THAI_C,    THAI_V  ),
        (THAI_V,    THAI_V  )
    ]
    
    widthHint = {
        SYMBOL:         1,
        LATIN:          1,
        CJK:            2,
        HANGLE:         2,
        THAI_C:         1
    }
    
    @classmethod
    def width(self, property, char):
        if property in self.widthHint:
            return self.widthHint[property]
        if property == self.THAI_V:
            if re.match(r'[\u0E33]', char):
                return 1
            else:
                return 0
        raise NotImplementedError


characterProperty = namedtuple('CharacterProperty', 'char prohibit')

class TextFolder(object):

    def getProhibitationProperty(self, char):
        for property, patterns in ProhibitationPropertySet.pattern.items():
            for regex in patterns:
                if re.match(regex, char):
                    return property
        return ProhibitationPropertySet.OTHERS

    def getCharacterProperty(self, char):
        for property, patterns in CharacterPropertySet.pattern.items():
            for regex in patterns:
                if re.match(regex, char):
                    return property
        return CharacterPropertySet.UNKNOWN

    def getProperty(self, char):
        return characterProperty(self.getCharacterProperty(char), self.getProhibitationProperty(char))

    def getCharacterWidth(self, char):
        return CharacterPropertySet.width(self.getCharacterProperty(char), char)

    def enableSplit(self, a, b):
        pa, pb = self.getProperty(a), self.getProperty(b)
        if (pa.prohibit, pb.prohibit) in ProhibitationPropertySet.inseparable:
            return False
        if (pa.prohibit, pb.prohibit) in ProhibitationPropertySet.separable:
            return True
        if (pa.char, pb.char) in CharacterPropertySet.inseparable:
            return False
        return True

    def splitText(self, text):
        for i in range(len(text) - 1):
            if self.enableSplit(text[i], text[i+1]):
                return text[:i+1], text[i+1:]
        return text, None

    def splitTextAll(self, text):
        result = []
        while True:
            s, text = self.splitText(text)
            result.append(s)
            if text is None:
                break
        return result

    
    def getDisplayWidth(self, text):
        return sum(map(self.getCharacterWidth, text))

    def foldtext(self, criteria, text):
        if isinstance(criteria, int):
            criteria = lambda x, w=criteria: self.getDisplayWidth(x) <= w
        result = []
        line = ''
        for token in self.splitTextAll(text):
            if not criteria(line + token):
                result.append(line)
                if self.getProhibitationProperty(token) == ProhibitationPropertySet.SEPARATION:
                    line = ''
                else:
                    line = token
            else:
                line += token
        result.append(line)
        return result


if __name__ == '__main__':

    TEST_DATA_JA = (u'1943 年における T-34 戦車の最終型です。3 人用の新型砲塔により、より強力な 85 mm 砲の'
        u'搭載を実現し、前型である T-34-76 に比べて大幅に戦力が向上していました。数種類の派生型を合わせて合計 35,000 '
        u'両以上が生産されており、一部の国々では今も現役車輌として配備されています。' )
    TEST_DATA_EN = (
        u'Final modification of the T-34 tank of 1943. A new three-man gun turret '
        u'allowed a more powerful 85-mm gun to be mounted. This greatly increased '
        u'the combat effectiveness of the tank compared to its predecessor, '
        u'the T-34-76. A total of more than 35,000, in several variants, were produced. '
        u'Today the tank is still in service in several countries.' )
    TEST_DATA_RU = (
        u'Является завершающей модификацией танка Т-34 образца 1943 г. Новая трёхместная '
        u'орудийная башня позволила установить более мощную 85-мм пушку. Это значительно '
        u'повысило боевую эффективность танка по сравнению с предшественником Т-34-76. '
        u'Всего было выпущено более 35 тысяч единиц различных модификаций. До настоящего '
        u'времени состоит на вооружении ряда стран.' )
    TEST_DATA_KR = (
        u'1943년 제작된 T-34의 최종 개량형이다. 3인 포탑을 탑재하여 강력한 85mm 주포를 장착할 수 있다. 이전 모델인 '
        u'T-34-76과 비교하여 전투 성능이 비약적으로 향상되었다. 변형 기종을 포함하여 총 35,000여 대가 생산되었다. '
        u'일부 국가에서는 아직도 실전에 사용 중이다.' )
    TEST_DATA_TW = (
        u'1943 年 T-34 戰車的最終修改型。新式的三人式炮塔允許安裝更為強大的 85 毫米炮管。與其前輩 T-34-76 '
        u'相比，大大地提高了戰車的作戰效率。各種型號共生產超過了 35,000 輛。時至今日，該戰車仍服役於幾個國家。' )
    TEST_DATA_TH = (
        u'รุ่นดัดแปลงสุดท้ายของ T-34 ในปี 1943 ป้อมปืนใหม่ที่รองรับพลรถถังสามคนทำให้สามารถติดตั้งปืน 85มม. ที่ทรงพลังกว่าเดิมบนรถถังได้ และยังเพิ่มประสิทธิภาพการรบให้กับรถถังอย่างมากเมื่อเทียบกับรุ่น '
        u'T-34-76 ที่ผลิตมาก่อน มียอดการผลิตโดยรวมรุ่นทั้งหมด 35,000 คันด้วยกัน ถึงทุกวันนี้รถถังรุ่นนี้ยังคงประจำการในหลายๆประเทศ' )
    TEST_DATA_VN = (
        u'Phiên bản chỉnh sửa cuối cùng của xe tăng T-34 vào năm 1943. Tháp pháo mới '
        u'có thể chứa 3 người, đồng thời lắp được nòng 85 mm cho hỏa lực mạnh hơn. '
        u'Điều này đã làm gia tăng đáng kể hiệu quả chiến đấu của xe khi so sánh với '
        u'mẫu tăng đời trước, T-34-76. Tổng cộng hơn 35 000 chiếc, tính cả một vài biến '
        u'thể, đã được sản xuất. Đến tận ngày nay, nó vẫn nằm trong biên chế quân đội '
        u'của một số quốc gia.' )
    TEST_DATA_ID = (
        u'Modifikasi akhir T-34 tahun 1943. Sebuah turret senjata tiga orang membuatnya '
        u'dapat menggunakan senjata 85 mm. Hal ini dengan drastis meningkatkan efektivitas '
        u'tempur tank dibandingkan dengan pendahulunya, T-34-76. Total lebih dari 35,000, '
        u'dalam beberapa varian, diproduksi. Saat ini tank masih masuk layanan militer di '
        u'beberapa negara.' )

    folder = TextFolder()
    print()
    print('\n'.join(folder.foldtext(72, TEST_DATA_JA)), '\n')
    print('\n'.join(folder.foldtext(72, TEST_DATA_EN)), '\n')
    print('\n'.join(folder.foldtext(72, TEST_DATA_RU)), '\n')
    print('\n'.join(folder.foldtext(72, TEST_DATA_TW)), '\n')
    print('\n'.join(folder.foldtext(72, TEST_DATA_KR)), '\n')
    print('\n'.join(folder.foldtext(72, TEST_DATA_TH)), '\n')
    print('\n'.join(folder.foldtext(72, TEST_DATA_VN)), '\n')
    print('\n'.join(folder.foldtext(72, TEST_DATA_ID)), '\n')
    
    #for token in folder.splitTextAll(TEST_DATA_TH):
    #    print('"{}": ({}), ({}), {}'.format(token, len(token), folder.getDisplayWidth(token),
    #        list(map(lambda x: hex(ord(x)), token))))
