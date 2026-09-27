#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鸿-代理 (h-agent) 三份代理材料生成脚本
依据湖北诚明律师事务所标准模板版式：
  标题二号(22pt)宋体加粗居中；正文仿宋四号(14pt)，行距约1.8；小节标题黑体15pt加粗
用法：python3 generate.py <输出目录> '<JSON>'
JSON 字段见 SKILL.md
"""
import json
import os
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Pt

FIRM = "湖北诚明律师事务所"
FIRM_ADDR = "武汉市黄孝河路竹叶山华中国际广场A座17楼"
FIRM_TEL = "（027）82623083"


def set_run(run, size=14, bold=False, font="仿宋", title=False):
    run.font.size = Pt(22 if title else size)
    run.font.bold = bold
    run.font.name = "宋体" if title else font
    r = run._element.rPr.rFonts
    r.set(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia",
        "宋体" if title else font,
    )


def para(doc, text="", size=14, bold=False, font="仿宋", title=False,
         align=None, indent=True, space_after=6):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.5
    pf.space_after = Pt(space_after)
    if align is not None:
        pf.alignment = align
    elif not title:
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent and not title and text:
        pf.first_line_indent = Pt(28)
    run = p.add_run(text)
    set_run(run, size=size, bold=bold, font=font, title=title)
    return p


def make_doc(title):
    doc = Document()
    return doc


def gen_contract(d, out):
    """委托代理合同（民事）"""
    lawyers = d["lawyers"]
    year = d["year"]
    doc = make_doc("contract")
    para(doc, f"（{year}）诚律民字第      号", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False, space_after=2)
    para(doc, "民事委托代理合同", title=True, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=14)

    para(doc, f"委托人（甲方）：{d['client_name']}", indent=False)
    para(doc, f"地　址：{d.get('client_address', '')}", indent=False)
    para(doc, f"电　话：{d.get('client_phone', '')}", indent=False)
    para(doc, f"受托人（乙方）：{FIRM}", indent=False)
    para(doc, f"地　址：{FIRM_ADDR}", indent=False)
    para(doc, f"电　话：{FIRM_TEL}", indent=False)

    para(doc, f"甲方因与{d['opponent']}{d['case_type']}一案，聘请乙方委派律师担任该案{d['stage']}阶段的诉讼代理人。经双方协商一致，达成如下协议：")

    items = [
        f"第一条、乙方接受甲方委托，指派 {lawyers} 律师担任该案的诉讼代理人。",
        "第二条、乙方律师应依法维护甲方的合法权益，履行代理职责。",
        "第三条、甲方应如实向律师陈述案情事实，提供本案的有关证据或线索。乙方接受委托后，若发现甲方捏造事实、隐瞒案情、弄虚作假的行为，有权书面通知解除本合同并终止代理，已收取的费用不予退还，由此引起的后果由甲方承担。",
        "第四条、乙方若无故终止代理，应将律师费全部退还甲方；如甲方单方终止委托，乙方已收取的费用不予退回。",
        "第五条、乙方律师的代理权限为：" + "；".join(
            f"{ln}（{au}）" for ln, au in zip(
                [s.strip() for s in re.split(r"[、，,]", lawyers) if s.strip()],
                d.get("lawyer_authorities", []),
            )
        ) + "。",
        f"第六条、根据《关于进一步规范律师服务收费的意见》（司发通〔2021〕87号）及《湖北省律师服务收费指导价标准（暂行）》的规定，乙方向甲方收取律师服务费人民币            元（大写：{d.get('fee_cn', '')}），于本合同签订之日起 {d.get('payment_days', '5')} 天内一次性付清。",
        "第七条、本合同自双方签字盖章之日起生效，至本委托事项终止之日止。本合同一式两份，甲乙双方各执一份，具有同等法律效力。",
    ]
    for t in items:
        para(doc, t)

    para(doc, "", indent=False)
    para(doc, "甲方（签字/盖章）：", indent=False)
    para(doc, "乙方（盖章）：", indent=False)
    para(doc, "承办律师（签名）：", indent=False)
    para(doc, "　　　　年　　月　　日", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    doc.save(out)


def gen_poal(d, out):
    """授权委托书"""
    doc = make_doc("poal")
    para(doc, "授权委托书", title=True, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=14)

    para(doc, f"委托人：{d['client_name']}", indent=False)
    para(doc, f"受托人：{d['lawyers']}，{FIRM}律师。", indent=False)
    if d.get("lawyer_phones"):
        para(doc, "联系电话：" + "、".join(d["lawyer_phones"]) + "。", indent=False)
    para(doc, f"委托人因与{d['opponent']}{d['case_type']}一案，委托上列受托人为本案{d['stage']}阶段的诉讼代理人。")
    auth = "；".join(
        f"{ln}的代理权限为{au}" for ln, au in zip(
            [s.strip() for s in re.split(r"[、，,]", d["lawyers"]) if s.strip()],
            d.get("lawyer_authorities", []),
        )
    )
    para(doc, f"代理权限：{auth}。")
    para(doc, "特别授权权限包括：代为承认、放弃、变更诉讼请求，进行和解、调解，提起反诉或者上诉，代收法律文书。")
    para(doc, "委托期限：自本委托书签署之日起至本案本阶段审理终结之日止。")
    para(doc, "", indent=False)
    para(doc, "委托人（签名/捺印）：", indent=False)
    para(doc, "　　　　年　　月　　日", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    doc.save(out)


def gen_letter(d, out):
    """律师事务所函"""
    doc = make_doc("letter")
    para(doc, f"（{d['year']}）诚律民字第      号", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False, space_after=2)
    para(doc, "律师事务所函", title=True, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=14)
    para(doc, f"{d.get('court', '　　　　　　人民法院：')}：", indent=False)
    para(doc, f"本所接受{d['client_name']}的委托，指派{d['lawyers']}律师担任其与{d['opponent']}{d['case_type']}一案{d['stage']}阶段的诉讼代理人。")
    auth = "；".join(
        f"{ln}（{au}）" for ln, au in zip(
            [s.strip() for s in re.split(r"[、，,]", d["lawyers"]) if s.strip()],
            d.get("lawyer_authorities", []),
        )
    )
    para(doc, f"代理权限：{auth}。")
    para(doc, "特此函告。")
    para(doc, "", indent=False)
    para(doc, f"{FIRM}（盖章）", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    para(doc, "　　　　年　　月　　日", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    para(doc, "", indent=False)
    para(doc, f"地址：{FIRM_ADDR}", indent=False, size=12)
    para(doc, f"电话：{FIRM_TEL}", indent=False, size=12)
    doc.save(out)


def main():
    if len(sys.argv) != 3:
        print("usage: generate.py <输出目录> '<JSON>'")
        sys.exit(1)
    outdir, payload = sys.argv[1], sys.argv[2]
    d = json.loads(payload)
    os.makedirs(outdir, exist_ok=True)
    outs = {
        "委托代理合同.docx": gen_contract,
        "授权委托书.docx": gen_poal,
        "律师事务所函.docx": gen_letter,
    }
    for name, fn in outs.items():
        path = os.path.join(outdir, name)
        fn(d, path)
        print("OK", path)


if __name__ == "__main__":
    main()
