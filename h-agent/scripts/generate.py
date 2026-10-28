#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鸿-代理 (h-agent) 三份代理材料生成脚本
沿用原模板版式：
  标题二号(22pt)宋体加粗居中；正文仿宋四号(14pt)，行距约1.8；小节标题黑体15pt加粗
用法：python3 generate.py <输出目录> <本地JSON文件>
JSON 字段见 SKILL.md
"""
import json
import os
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Pt




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
    para(doc, f"（{year}）{d['firm']['document_prefix']}第      号", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False, space_after=2)
    para(doc, "民事委托代理合同", title=True, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_after=14)

    para(doc, f"委托人（甲方）：{d['client_name']}", indent=False)
    para(doc, f"地　址：{d.get('client_address', '')}", indent=False)
    para(doc, f"电　话：{d.get('client_phone', '')}", indent=False)
    para(doc, f"受托人（乙方）：{d['firm']['name']}", indent=False)
    para(doc, f"地　址：{d['firm']['address']}", indent=False)
    para(doc, f"电　话：{d['firm']['phone']}", indent=False)

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
        f"第六条、{d['firm']['fee_basis_text']}乙方向甲方收取律师服务费人民币{d['fee_amount']}元（大写：{d.get('fee_cn', '')}），于本合同签订之日起 {d.get('payment_days', '5')} 天内一次性付清。",
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
    para(doc, f"受托人：{d['lawyers']}，{d['firm']['name']}律师。", indent=False)
    if d.get("lawyer_phones"):
        para(doc, "联系电话：" + "；".join(f"{a['name']}：{a['phone']}" for a in d["agents"]) + "。", indent=False)
    para(doc, f"委托人因与{d['opponent']}{d['case_type']}一案，委托上列受托人为本案{d['stage']}阶段的诉讼代理人。")
    auth = "；".join(
        f"{ln}的代理权限为{au}" for ln, au in zip(
            [s.strip() for s in re.split(r"[、，,]", d["lawyers"]) if s.strip()],
            d.get("lawyer_authorities", []),
        )
    )
    para(doc, f"代理权限：{auth}。")
    for lawyer in d['agents']:
        if lawyer['authority'] == '特别授权':
            para(doc, f"{lawyer['name']}的特别授权事项：{lawyer['authority_text']}。")
    para(doc, "委托期限：自本委托书签署之日起至本案本阶段审理终结之日止。")
    para(doc, "", indent=False)
    para(doc, "委托人（签名/捺印）：", indent=False)
    para(doc, "　　　　年　　月　　日", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    doc.save(out)


def gen_letter(d, out):
    """律师事务所函"""
    doc = make_doc("letter")
    para(doc, f"（{d['year']}）{d['firm']['document_prefix']}第      号", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False, space_after=2)
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
    para(doc, f"{d['firm']['name']}（盖章）", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    para(doc, "　　　　年　　月　　日", align=WD_ALIGN_PARAGRAPH.RIGHT, indent=False)
    para(doc, "", indent=False)
    para(doc, f"地址：{d['firm']['address']}", indent=False, size=12)
    para(doc, f"电话：{d['firm']['phone']}", indent=False, size=12)
    doc.save(out)


def validate(d):
    """先校验后写文件。确认标记由 agent 在本轮用户核对后写入，不能证明现实身份。"""
    if d.get('confirmed') is not True or d.get('template_confirmed') is not True:
        raise ValueError('必须先核对案件信息并确认采用该合同模板')
    for key in ('year', 'client_name', 'client_address', 'client_phone', 'opponent',
                'case_type', 'stage', 'court', 'fee_amount', 'fee_cn', 'payment_days'):
        if not isinstance(d.get(key), str) or not d[key].strip():
            raise ValueError(f'缺少字段：{key}')
    if d['stage'] not in ('一审', '二审'):
        raise ValueError('当前内置合同仅支持民事一审、二审；其他程序请提供对应模板')
    if not re.fullmatch(r'\d{4}', d['year']):
        raise ValueError('年份应为四位数字')
    if not re.fullmatch(r'\d+(?:\.\d{1,2})?', d['fee_amount']):
        raise ValueError('费用需为非负数字，最多两位小数')
    if not d['payment_days'].isdigit() or int(d['payment_days']) < 1:
        raise ValueError('付款天数需为正整数')
    firm = d.get('firm', {})
    for key in ('name', 'address', 'phone', 'document_prefix'):
        if not isinstance(firm.get(key), str) or not firm[key].strip():
            raise ValueError(f'缺少律所配置：{key}')
    if not isinstance(firm.get('fee_basis_text'), str):
        raise ValueError('fee_basis_text 须由用户或模板提供，可明确为空')
    agents = d.get('agents')
    if not isinstance(agents, list) or not agents:
        raise ValueError('至少提供一位代理律师')
    names = set()
    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError('每位律师需为独立对象')
        for key in ('name', 'phone', 'authority'):
            if not isinstance(agent.get(key), str) or not agent[key].strip():
                raise ValueError(f'缺少律师字段：{key}')
        if agent['name'] in names:
            raise ValueError('律师姓名重复，请核对')
        names.add(agent['name'])
        if agent['authority'] not in ('一般授权', '特别授权'):
            raise ValueError('代理权限须明确为一般授权或特别授权')
        if agent['authority'] == '特别授权' and not agent.get('authority_text', '').strip():
            raise ValueError('特别授权须逐位提供经用户确认的具体事项')
    # 只做字符及长度检查，不声称核验号码归属或实际身份。
    for phone in [d['client_phone'], firm['phone']] + [a['phone'] for a in agents]:
        digits = re.sub(r'[^0-9]', '', phone)
        if not re.fullmatch(r'[+0-9()（） \-]+', phone) or not 7 <= len(digits) <= 18:
            raise ValueError('电话格式需核对；分机请另行说明')
    d['lawyers'] = '、'.join(a['name'] for a in agents)
    d['lawyer_phones'] = [a['phone'] for a in agents]
    d['lawyer_authorities'] = [a['authority'] for a in agents]
    return d


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: generate.py <输出目录> <本地JSON文件>')
    outdir, input_path = sys.argv[1:]
    with open(input_path, encoding='utf-8') as f:
        d = validate(json.load(f))
    outs = {'委托代理合同.docx': gen_contract, '授权委托书.docx': gen_poal,
            '律师事务所函.docx': gen_letter}
    if any(os.path.exists(os.path.join(outdir, name)) for name in outs):
        raise SystemExit('目标文件已存在，请使用新的输出目录')
    os.makedirs(outdir, exist_ok=True)
    for name, fn in outs.items():
        fn(d, os.path.join(outdir, name))
    print('已生成三份材料；请回读字段、核对金额并检查分页后交付。')


if __name__ == '__main__':
    main()
