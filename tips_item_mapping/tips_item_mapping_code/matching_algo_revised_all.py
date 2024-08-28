from fuzzywuzzy import fuzz
from item_mapping import *

#config

stopwords = {'배변패드', '강아지', '강아지패드', '배변용품', '기저귀'}
top_1st = {'애견', '반려견', '강아지', '화장실', '강아지화장실', '강아지배변판', 
           '기저귀','팬티', '배변', '애견패드', '강아지배변패드',  '강아지배변패드애견패드',
            '애견용품', '강아지용품', '배변용품', '위생용품', '용품', '패드', '고양이',
            '국산',' 국내산' , '현대Hmall', '(남녀선택)', '핏', '썸머'}

# diaper_size
# size_unit도 잘 보고 조정해야 함
size_units = {
    'XS' : 0,
    'NB' : 0, # 신생아
    '신생아용' : 0,
    '신생아형' : 0, 
    '신생아': 0,
    '1단계' : 0,
    '뉴본' : 0,

    '소형패드' : 1,
    '소형' : 1,
    'S' : 1,
    '2단계' : 1,

    '중형패드': 2,
    '중형' : 2,
    'M' : 2,
    '3단계' : 2,

    '대형패드' : 3,
    '대형' : 3,
    'L' : 3, 
    '4단계' : 3,

    '초대형' : 4,
    '초대형패드' : 4,
    '특대형' : 4,
    '특대형패드' : 4,
    'XL': 4,
    '5단계' : 4,
    
    '점보형' : 5,
    'JB' : 5,
    'XXL': 5, 
    '6단계' : 5,

    '키즈형' : 6,
    '키즈' : 6,
    '빅형': 6,
    '3XL' : 6,
    'XXXL' : 6, 
    '7단계' : 6
}

# diaper size
type_units = {
    '일자형' : 0,
    '밴드형' : 1,
    '팬티형' : 2
}

# 0. item명에 매수가 있다면 그 수를 반환
def retreive_amount(item):
    for i in item:
        if any(char.isdigit() for char in i) and (('매' in i) or ('개' in i) or ('p' in i.lower()) or ('ea' in i.lower())): 
            amount = []
            for index, char in enumerate(i):
                if ((char.lower() == 'x') or (char.lower() == '*'))  and index >= 2: # Modify to select the first one after splitting in the relevant unit
                    break
                if char.isdigit():
                    amount.append(char)
            amount = int(''.join(amount))
            break
        else:
            amount = None
    return amount


# 1. 양(g)이 있다면 그 수를 반환
def retreive_quant(item):
    for i in item:
        if any(char.isdigit() for char in i) and 'g' in i:
            quant = i
            break
        else:
            quant = None
    return quant


# 2. 사이즈가 있다면 그 사이즈를 반환 => 패드 + 간식 + 기저귀
def retreive_size(item, size_units = size_units):
    for i in item:
        if i in size_units:
            sizeunit = i
            size = size_units[i]
            break
        else:
            sizeunit = ""
            size = None
    return sizeunit, size

# 3. 종류가 있다면 그 종류를 반환 => 기저귀 종류
def retreive_type(item, type_units = type_units):
    for i in item:
        if i in type_units:
            typeunit = i
            types = type_units[i]
            break 
        else:
            typeunit = ""
            types = None
    return typeunit, types

# 위를 제외한 나머지를 fuzzy ratio로 비교
def get_seq(item, brand, sizeunit, typeunit, top_1st=top_1st):

    thr = 49 # thr을 좀 더 높이면 nsame까지 거를 수 있을 것 같음
    filtered_item = []
    #filtered_item = item

    # for i in item:
    #     if not(any(char.isdigit() for char in i) or (brand in i) or (i == sizeunit) or (i == typeunit) or (i in stopwords)): 
    #         filtered_item.append(i)

    for i in item:
        if not((brand in i) or (i == sizeunit) or (i == typeunit) or (i in stopwords)): 
            filtered_item.append(i)

    seq = ''
    if len(item) > 3: 
        for i in filtered_item:
            if i not in top_1st: 
                seq += i + ' '
    else:
        seq = ' '.join(filtered_item)

    if len(seq.split()) < 3 :
        seq = ' '.join(item) # if words lost too much, return as it was
        thr = 30
    return seq, thr

# 위의 함수들을 활용해서 단계별로 item matching을 진행하는 최종 함수
def check_same_item(row): 
    item1 = [strip_special_characters(word) for word in row['item1'].split()]
    item2 = [strip_special_characters(word) for word in row['item2'].split()]
    brand1 = row['brand1']
    brand2 = row['brand2']

    #### === 0. Check brand ==================================================================
    if brand1 != brand2 :
        res = 'different brand'
        return 'F', res
    
    ### === 1. check the mount ===============================================================
    amount1 = retreive_amount(item1)
    amount2 = retreive_amount(item2)

    if amount1 != amount2 :
        # if 매수가 두개가 존재하는데 배수가 아닐경우 다른 아이템, 함수 종료
        if ((amount1 and amount2)):
            large = max(amount1, amount2)
            small = min(amount1, amount2)
            if (large % small != 0):
                return "F" , {'매수1' : amount1, '매수2': amount2}
        # else 매수 정보가 하나라도 없거나, 둘다없거나, 두개가 일치할 경우 다음 스텝

    ### === 2. check the quantity (gram) ==> 그램 정보가 둘다 존재하면 하드하게 분류하고 종료 ==========
    quant1 = retreive_quant(item1)
    quant2 = retreive_quant(item2)

    if (quant1 and quant2):
        if quant1 != quant2 :
            # 중량 정보가 하나만 있으면 서로 다른 상품 (매치 불가하므로 F처리)
            return "F" , {'중량1' : quant1, '중량2': quant2}
        else :
            # 중량이 둘다 존재하고 일치할때, 많은 브랜드의 경우 중량 == 상품라인이므로 True (정직한패드)
            return "T",  {'중량1' : quant1, '중량2': quant2}

    ### ===== 3. check the size ========================================================================
    sizeunit1, size1 = retreive_size(item1)
    sizeunit2, size2 = retreive_size(item2)

    if (((size1) and (size2)) and (size1 != size2)) :
        return "F" , {'사이즈1' : size1, '사이즈2': size2, '중량1' : quant1, '중량2': quant2, '매수1' : amount1, '매수2': amount2}

    ### ===== 4. check the type ========================================================================
    typeunit1, type1 = retreive_type(item1)
    typeunit2, type2 = retreive_type(item2)

    if (((type1) and (type2)) and (type1 != type2)) : 
        return "F" , {'종류1' : type1, '종류2': type2, '사이즈1' : size1, '사이즈2' : size2}

    ### ===== 5. check text =============================================================================
    seq1, thr = get_seq(item1, brand1, sizeunit1, typeunit1)
    seq2, _ = get_seq(item2, brand2, sizeunit2, typeunit2)

    similarity = fuzz.ratio(seq1.upper(), seq2.upper())

    if similarity > thr :
        return "T" , {'seq1' : seq1, 'seq2': seq2, 'sim': similarity, '사이즈1' : size1, '사이즈2': size2, '종류1' : type1, '종류2': type2, '중량1' : quant1, '중량2': quant2, '매수1' : amount1, '매수2': amount2}
    else : 
        return "F" , {'seq1' : seq1, 'seq2': seq2, 'sim': similarity, '사이즈1' : size1, '사이즈2': size2, '종류1' : type1, '종류2': type2, '중량1' : quant1, '중량2': quant2, '매수1' : amount1, '매수2': amount2}

