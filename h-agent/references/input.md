# 本地输入结构

所有值由本次用户填写并核对。以下仅为结构，不是可直接执行的数据；不提供真实人员示例。

- confirmed：最终核对答复后设为 true。
- template_confirmed：用户确认采用内置合同条款后设为 true。
- year、client_name、client_address、client_phone、opponent、case_type、stage、court：非空字符串。
- fee_amount：以元为单位的数字字符串，最多两位小数。fee_cn：对应人民币大写；agent 必须核对二者，脚本不自动核验大写金额。
- payment_days：正整数字符串。
- firm：对象，包含 name、address、phone、document_prefix、fee_basis_text。收费依据必须来自本所认可文本，可明确为空；不从网上拼接条款。
- agents：对象数组，每个对象含 name、phone、authority；authority 取一般授权或特别授权，后者必须同时提供 authority_text 具体事项。电话与姓名在同一对象绑定。

将输入保存为当前案件工作目录的本地 JSON 文件，不把含个人信息的 JSON 拼接进 shell 参数。调用时用安全参数数组；终端调用须正确引用路径：

```bash
python3 "<skill目录>/scripts/generate.py" "<新输出目录>" "<本地输入.json>"
```

Python 3 依赖 python-docx。脚本先校验再写文件，现有同名文件存在则拒绝覆盖。输入缺失、电话号码明显异常、权限未细化均拒绝生成。不得为绕过校验伪造占位姓名或电话。
