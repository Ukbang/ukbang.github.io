import xml.etree.ElementTree as ET
import copy
import os

# 아이콘 이름 목록 (순서대로: 좌→우, 위→아래)
ICON_NAMES = [
    "ai_brain", "ai_agent", "neural_net", "llm_chat", "training_data",
    "vision", "voice_ai", "ai_chip", "rag_search", "automation",
    "prompt", "transformer", "knowledge_graph", "rlhf", "embeddings"
]

# 아이콘 카드 크기 및 위치 (x, y, width=100, height=100)
# 5열 3행 구조: x = 20,140,260,380,500 / y = 20,160,300
ICON_POSITIONS = []
for row, y in enumerate([20, 160, 300]):
    for col, x in enumerate([20, 140, 260, 380, 500]):
        ICON_POSITIONS.append((x, y, 100, 100))

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

def in_bounds(elem, x, y, w, h, margin=2):
    """요소가 카드 영역 안에 있는지 확인"""
    def get_float(attr, default=0):
        try:
            return float(elem.get(attr, default))
        except:
            return default

    tag = elem.tag.replace(f"{{{NS}}}", "")

    ex, ey = None, None

    if tag in ("rect", "image"):
        ex = get_float("x")
        ey = get_float("y")
    elif tag in ("circle", "ellipse"):
        ex = get_float("cx")
        ey = get_float("cy")
    elif tag in ("line",):
        ex = get_float("x1")
        ey = get_float("y1")
    elif tag == "text":
        ex = get_float("x")
        ey = get_float("y")
    elif tag in ("path", "polyline", "polygon"):
        d = elem.get("d") or elem.get("points") or ""
        nums = []
        import re
        for n in re.findall(r"-?\d+\.?\d*", d):
            nums.append(float(n))
        if len(nums) >= 2:
            ex, ey = nums[0], nums[1]

    if ex is None:
        return False

    return (x - margin <= ex <= x + w + margin) and (y - margin <= ey <= y + h + margin)

def extract_icon(tree_root, ix, iy, iw, ih, name, output_dir):
    """특정 영역의 요소들만 추출해서 개별 SVG로 저장"""
    # 새 SVG 루트
    new_svg = ET.Element("svg")
    new_svg.set("xmlns", NS)
    new_svg.set("width", "100")
    new_svg.set("height", "100")
    new_svg.set("viewBox", f"{ix} {iy} {iw} {ih}")

    # defs 복사 (style, marker 등)
    for child in tree_root:
        tag = child.tag.replace(f"{{{NS}}}", "")
        if tag == "defs":
            new_svg.append(copy.deepcopy(child))
            break

    # 해당 영역 요소 복사
    for child in tree_root:
        tag = child.tag.replace(f"{{{NS}}}", "")
        if tag in ("defs",):
            continue
        if in_bounds(child, ix, iy, iw, ih):
            new_svg.append(copy.deepcopy(child))

    # 저장
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{name}.svg")
    tree = ET.ElementTree(new_svg)
    ET.indent(tree, space="  ")
    tree.write(out_path, encoding="unicode", xml_declaration=False)
    print(f"  저장됨: {out_path}")

def main():
    input_file = "ai_line_icons.svg"
    output_dir = "icons_output"

    if not os.path.exists(input_file):
        print(f"오류: '{input_file}' 파일을 찾을 수 없어요.")
        print("split_icons.py와 같은 폴더에 ai_line_icons.svg를 저장해 주세요.")
        return

    tree = ET.parse(input_file)
    root = tree.getroot()

    print(f"총 {len(ICON_NAMES)}개 아이콘 추출 시작...\n")

    for i, (name, pos) in enumerate(zip(ICON_NAMES, ICON_POSITIONS)):
        ix, iy, iw, ih = pos
        print(f"[{i+1:02d}] {name}")
        extract_icon(root, ix, iy, iw, ih, name, output_dir)

    print(f"\n완료! '{output_dir}/' 폴더에 저장됐어요.")

if __name__ == "__main__":
    main()
