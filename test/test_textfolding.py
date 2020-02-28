
import unittest

from lib.textfolding import TextFolder, CharacterPropertySet, ProhibitationPropertySet


TEST_DATA_JA = (
    u'1943 年における T-34 戦車の最終型です。3 人用の新型砲塔により、より強力な 85 mm 砲の搭載を実現し、'
    u'前型である T-34-76 に比べて大幅に戦力が向上していました。数種類の派生型を合わせて合計 35,000 両以上が生産されており、'
    u'一部の国々では今も現役車輌として配備されています。' )
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

RESULT_DATA_JA = ['1943', ' ', '年', 'に', 'お', 'け', 'る', ' ', 'T-34', ' ', '戦', '車', 'の', '最', '終',
    '型', 'で', 'す。', '3', ' ', '人', '用', 'の', '新', '型', '砲', '塔', 'に', 'よ', 'り、', 'よ', 'り', '強',
    '力', 'な', ' ', '85', ' ', 'mm', ' ', '砲', 'の', '搭', '載', 'を', '実', '現', 'し、', '前', '型', 'で',
    'あ', 'る', ' ', 'T-34-76', ' ', 'に', '比', 'べ', 'て', '大', '幅', 'に', '戦', '力', 'が', '向', '上',
    'し', 'て', 'い', 'ま', 'し', 'た。', '数', '種', '類', 'の', '派', '生', '型', 'を', '合', 'わ', 'せ', 'て',
    '合', '計', ' ', '35,000', ' ', '両', '以', '上', 'が', '生', '産', 'さ', 'れ', 'て', 'お', 'り、', '一',
    '部', 'の', '国', '々', 'で', 'は', '今', 'も', '現', '役', '車', '輌', 'と', 'し', 'て', '配', '備', 'さ',
    'れ', 'て', 'い', 'ま', 'す。']
RESULT_DATA_EN = ['Final', ' ', 'modification', ' ', 'of', ' ', 'the', ' ', 'T-34', ' ', 'tank', ' ',
    'of', ' ', '1943.', ' ', 'A', ' ', 'new', ' ', 'three-man', ' ', 'gun', ' ', 'turret', ' ',
    'allowed', ' ', 'a', ' ', 'more', ' ', 'powerful', ' ', '85-mm', ' ', 'gun', ' ', 'to', ' ',
    'be', ' ', 'mounted.', ' ', 'This', ' ', 'greatly', ' ', 'increased', ' ', 'the', ' ', 'combat',
    ' ', 'effectiveness', ' ', 'of', ' ', 'the', ' ', 'tank', ' ', 'compared', ' ', 'to', ' ', 'its',
    ' ', 'predecessor,', ' ', 'the', ' ', 'T-34-76.', ' ', 'A', ' ', 'total', ' ', 'of', ' ', 'more',
    ' ', 'than', ' ', '35,000,', ' ', 'in', ' ', 'several', ' ', 'variants,', ' ', 'were', ' ',
    'produced.', ' ', 'Today', ' ', 'the', ' ', 'tank', ' ', 'is', ' ', 'still', ' ', 'in', ' ',
    'service', ' ', 'in', ' ', 'several', ' ', 'countries.']
RESULT_DATA_RU = ['Является', ' ', 'завершающей', ' ', 'модификацией', ' ', 'танка', ' ', 'Т-34', ' ',
    'образца', ' ', '1943', ' ', 'г.', ' ', 'Новая', ' ', 'трёхместная', ' ', 'орудийная', ' ',
    'башня', ' ', 'позволила', ' ', 'установить', ' ', 'более', ' ', 'мощную', ' ', '85-мм', ' ',
    'пушку.', ' ', 'Это', ' ', 'значительно', ' ', 'повысило', ' ', 'боевую', ' ', 'эффективность',
    ' ', 'танка', ' ', 'по', ' ', 'сравнению', ' ', 'с', ' ', 'предшественником', ' ', 'Т-34-76.', ' ',
    'Всего', ' ', 'было', ' ', 'выпущено', ' ', 'более', ' ', '35', ' ', 'тысяч', ' ', 'единиц', ' ',
    'различных', ' ', 'модификаций.', ' ', 'До', ' ', 'настоящего', ' ', 'времени', ' ', 'состоит', ' ',
    'на', ' ', 'вооружении', ' ', 'ряда', ' ', 'стран.']

RESULT_FOLDING_TEXT_JA = [
    u'1943 年における T-34 戦車の最終型です。3 人用の新型砲塔によ',
    u'り、より強力な 85 mm 砲の搭載を実現し、前型である T-34-76 に',
    u'比べて大幅に戦力が向上していました。数種類の派生型を合わせて',
    u'合計 35,000 両以上が生産されており、一部の国々では今も現役車',
    u'輌として配備されています。' ]
RESULT_FOLDING_TEXT_EN = [
    u'Final modification of the T-34 tank of 1943. A new three-man',
    u'gun turret allowed a more powerful 85-mm gun to be mounted. ',
    u'This greatly increased the combat effectiveness of the tank ',
    u'compared to its predecessor, the T-34-76. A total of more ',
    u'than 35,000, in several variants, were produced. Today the ',
    u'tank is still in service in several countries.' ]
RESULT_FOLDING_TEXT_RU = [
    u'Является завершающей модификацией танка Т-34 образца 1943 г.',
    u'Новая трёхместная орудийная башня позволила установить более',
    u'мощную 85-мм пушку. Это значительно повысило боевую ',
    u'эффективность танка по сравнению с предшественником Т-34-76.',
    u'Всего было выпущено более 35 тысяч единиц различных ',
    u'модификаций. До настоящего времени состоит на вооружении ',
    u'ряда стран.' ]


class TextFolderTestCase(unittest.TestCase):

    def test_getProperty(self):
        f = TextFolder()
        C = CharacterPropertySet
        P = ProhibitationPropertySet
        self.assertEqual((C.LATIN, P.SEPARATION), f.getProperty(' '))
        self.assertEqual((C.LATIN, P.OTHERS), f.getProperty('3'))
        self.assertEqual((C.LATIN, P.OTHERS), f.getProperty('A'))
        self.assertEqual((C.CJK, P.OTHERS), f.getProperty('漢字'))
        self.assertEqual((C.CJK, P.OTHERS), f.getProperty('ひらがな'))
        self.assertEqual((C.CJK, P.OTHERS), f.getProperty('カタカナ'))
        self.assertEqual((C.LATIN, P.NOT_END), f.getProperty('('))
        self.assertEqual((C.LATIN, P.NOT_START), f.getProperty(')'))
        self.assertEqual((C.LATIN, P.NOT_START), f.getProperty('.'))
        self.assertEqual((C.LATIN, P.NOT_START), f.getProperty(','))
        self.assertEqual((C.CJK, P.NOT_END), f.getProperty('（'))
        self.assertEqual((C.CJK, P.NOT_START), f.getProperty('）'))
        self.assertEqual((C.CJK, P.NOT_START), f.getProperty('。'))
        self.assertEqual((C.CJK, P.NOT_START), f.getProperty('、'))

    def test_splitTextAll(self):
        f = TextFolder()
        self.assertEqual(RESULT_DATA_JA, f.splitTextAll(TEST_DATA_JA))
        self.assertEqual(RESULT_DATA_EN, f.splitTextAll(TEST_DATA_EN))
        self.assertEqual(RESULT_DATA_RU, f.splitTextAll(TEST_DATA_RU))

    def test_foldText(self):
        f = TextFolder()
        self.assertEqual(RESULT_FOLDING_TEXT_JA, f.foldtext(60, TEST_DATA_JA))
        self.assertEqual(RESULT_FOLDING_TEXT_EN, f.foldtext(60, TEST_DATA_EN))
        self.assertEqual(RESULT_FOLDING_TEXT_RU, f.foldtext(60, TEST_DATA_RU))

    def test_getDisplayWidth(self):
        f = TextFolder()
        data = u'1943 年における T-34 戦車の最終型です。'
        self.assertEqual((39, 25), (f.getDisplayWidth(data), len(data)))

    def test_getDisplayWidth_Thai(self):
        f = TextFolder()
        data = [ u'น', u'ดั', u'รุ่', u'จำ' ]
        self.assertEqual((1, 1), (f.getDisplayWidth(data[0]), len(data[0])))    # 1 chars
        self.assertEqual((1, 2), (f.getDisplayWidth(data[1]), len(data[1])))    # 2 chars
        self.assertEqual((1, 3), (f.getDisplayWidth(data[2]), len(data[2])))    # 3 chars
        self.assertEqual((2, 2), (f.getDisplayWidth(data[3]), len(data[3])))    # 2 chars
