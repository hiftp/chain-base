# -*- coding: utf-8 -*-

RELEASE_LEVELS = [ALPHA, BETA, RELEASE_CANDIDATE, FINAL] = [
    "alpha",
    "beta",
    "candidate",
    "final",
]
RELEASE_LEVELS_DISPLAY = {
    ALPHA: ALPHA,
    BETA: BETA,
    RELEASE_CANDIDATE: "rc",
    FINAL: "正式版",
}

RELEASE_ARCHS = [X64, X86] = ["64bit", "32bit"]

RELEASE_ARCH_DISPLAY = {X64: "64位", X86: "32位"}

# version_info format: (MAJOR, MINOR, MICRO, RELEASE_LEVEL, ARCH)
# properly comparable using normal operarors, for example:
#  (6,1,0,'beta',0) < (6,1,0,'candidate',1) < (6,1,0,'candidate',2)
#  (6,1,0,'candidate',2) < (6,1,0,'final',0) < (6,1,2,'final',0)
version_info = (0, 1, 0, FINAL, X64, "")
version = (
    ".".join(str(s) for s in version_info[:3])
    + f"({RELEASE_LEVELS_DISPLAY[version_info[3]]}) ({RELEASE_ARCH_DISPLAY[version_info[4]]}){version_info[5]}"
)
series = serie = major_version = ".".join(str(s) for s in version_info[:3])

product_name = "CAP"
description = "CAP-智能工业大数据-过程数据分析平台"
long_desc = """CAP-智能工业大数据-过程数据分析平台
"""

portal_url = "https://www.ethermeta.com.cn"
author = "EtherMeta Co. Ltd"
terms_url = "https://www.ethermeta.com.cn"
sla_url = "https://www.ethermeta.com.cn"
privacy_policy_url = "https://www.ethermeta.com.cn"
author_email = "info@ethermeta.com.cn"

classifiers = f"""
VHLS-Tightening Location SpotPoint\n\n
© 2015-2022 [{author}]({portal_url})。保留所有权利。\n\n
[帮助和学习](https://www.baidu.com)\n\n
[声明条款]({terms_url})-[隐私条款]({privacy_policy_url})-[服务协议]({sla_url})
"""

nt_service_name = "vhls-server-" + series.replace("~", "-")
