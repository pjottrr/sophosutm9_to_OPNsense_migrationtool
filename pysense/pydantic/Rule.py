from enum import Enum
from typing import Optional, List
from pydantic import Field
from pysense.pydantic.pydantic_base import BoolAsIntMixin, UIAwareMixin



class Rule(BoolAsIntMixin, UIAwareMixin):
    """
    Generated model for Rule for OPNsense
    """

    class RulesRuleStatetypeEnum(str, Enum):
        KEEP = "keep"
        SLOPPY = "sloppy"
        MODULATE = "modulate"
        SYNPROXY = "synproxy"
        NONE = "none"

    class RulesRuleStatePolicyEnum(str, Enum):
        IF_BOUND = "if-bound"
        FLOATING = "floating"

    class RulesRuleActionEnum(str, Enum):
        PASS = "pass"
        BLOCK = "block"
        REJECT = "reject"

    class RulesRuleDirectionEnum(str, Enum):
        IN = "in"
        OUT = "out"

    class RulesRuleIpprotocolEnum(str, Enum):
        INET = "inet"
        INET6 = "inet6"
        INET46 = "inet46"

    class RulesRuleIcmptypeEnum(str, Enum):
        ECHOREQ = "echoreq"
        ECHOREP = "echorep"
        UNREACH = "unreach"
        SQUENCH = "squench"
        REDIR = "redir"
        ALTHOST = "althost"
        ROUTERADV = "routeradv"
        ROUTERSOL = "routersol"
        TIMEX = "timex"
        PARAMPROB = "paramprob"
        TIMEREQ = "timereq"
        TIMEREP = "timerep"
        INFOREQ = "inforeq"
        INFOREP = "inforep"
        MASKREQ = "maskreq"
        MASKREP = "maskrep"

    class RulesRulePrioEnum(str, Enum):
        OPT1 = "1"
        OPT0 = "0"
        OPT2 = "2"
        OPT3 = "3"
        OPT4 = "4"
        OPT5 = "5"
        OPT6 = "6"
        OPT7 = "7"

    class RulesRuleSetPrioEnum(str, Enum):
        OPT1 = "1"
        OPT0 = "0"
        OPT2 = "2"
        OPT3 = "3"
        OPT4 = "4"
        OPT5 = "5"
        OPT6 = "6"
        OPT7 = "7"

    class RulesRuleSetPrioLowEnum(str, Enum):
        OPT1 = "1"
        OPT0 = "0"
        OPT2 = "2"
        OPT3 = "3"
        OPT4 = "4"
        OPT5 = "5"
        OPT6 = "6"
        OPT7 = "7"

    class RulesRuleTcpflags1Enum(str, Enum):
        SYN = "syn"
        ACK = "ack"
        FIN = "fin"
        RST = "rst"
        PSH = "psh"
        URG = "urg"
        ECE = "ece"
        CWR = "cwr"

    class RulesRuleTcpflags2Enum(str, Enum):
        SYN = "syn"
        ACK = "ack"
        FIN = "fin"
        RST = "rst"
        PSH = "psh"
        URG = "urg"
        ECE = "ece"
        CWR = "cwr"
    
    enabled: bool = Field(default=True)
    statetype: RulesRuleStatetypeEnum = Field(default=RulesRuleStatetypeEnum.KEEP)
    state_policy: Optional[RulesRuleStatePolicyEnum] = Field(default=None, alias="state-policy")
    sequence: int = Field(default=1, ge=1, le=999999, description="Sequence shall be between 1 and 999999.")
    sort_order: Optional[str] = None
    prio_group: Optional[str] = None
    action: RulesRuleActionEnum = Field(default=RulesRuleActionEnum.PASS)
    quick: bool = Field(default=True)
    interfacenot: bool = Field(default=False)
    interface: List[str] = Field(default_factory=list)
    direction: RulesRuleDirectionEnum = Field(default=RulesRuleDirectionEnum.IN)
    ipprotocol: RulesRuleIpprotocolEnum = Field(default=RulesRuleIpprotocolEnum.INET)
    protocol: str = Field(default="any")
    icmptype: List[RulesRuleIcmptypeEnum] = Field(default_factory=list)
    source_net: List[str] = Field(default=["any"])
    source_not: bool = Field(default=False)
    source_port: Optional[str] = Field(default=None, description="Please specify a valid portnumber, name, alias or range.")
    destination_net: List[str] = Field(default=["any"])
    destination_not: bool = Field(default=False)
    destination_port: Optional[str] = Field(default=None, description="Please specify a valid portnumber, name, alias or range.")
    gateway: Optional[str] = Field(default=None, description="Specify a valid gateway from the list matching the networks ip protocol.")
    replyto: Optional[str] = Field(default=None, description="Specify a valid gateway from the list matching the networks ip protocol.")
    disablereplyto: bool = Field(default=False)
    log: bool = Field(default=False)
    allowopts: bool = Field(default=False)
    nosync: bool = Field(default=False)
    nopfsync: bool = Field(default=False)
    statetimeout: Optional[int] = Field(default=None, ge=1, le=2147483647)
    udp_first: Optional[int] = Field(default=None, ge=1, le=2147483647, alias="udp-first")
    udp_multiple: Optional[int] = Field(default=None, ge=1, le=2147483647, alias="udp-multiple")
    udp_single: Optional[int] = Field(default=None, ge=1, le=2147483647, alias="udp-single")
    max_src_nodes: Optional[int] = Field(default=None, ge=1, le=2147483647, alias="max-src-nodes")
    max_src_states: Optional[int] = Field(default=None, ge=1, le=2147483647, alias="max-src-states")
    max_src_conn: Optional[int] = Field(default=None, ge=1, le=2147483647, alias="max-src-conn")
    max: Optional[int] = Field(default=None, ge=1, le=2147483647)
    max_src_conn_rate: Optional[int] = Field(default=None, ge=1, le=2147483647, alias="max-src-conn-rate")
    max_src_conn_rates: Optional[int] = Field(default=None, ge=1, le=2147483647, alias="max-src-conn-rates")
    overload: Optional[str] = Field(default=None, description="Alias not found.")
    adaptivestart: Optional[int] = Field(default=None, ge=0, le=2147483647)
    adaptiveend: Optional[int] = Field(default=None, ge=0, le=2147483647)
    prio: Optional[RulesRulePrioEnum] = None
    set_prio: Optional[RulesRuleSetPrioEnum] = Field(default=None, alias="set-prio")
    set_prio_low: Optional[RulesRuleSetPrioLowEnum] = Field(default=None, alias="set-prio-low")
    tag: Optional[str] = Field(default=None, pattern=r"^([0-9a-zA-Z.,_\-]){0,512}$")
    tagged: Optional[str] = Field(default=None, pattern=r"^([0-9a-zA-Z.,_\-]){0,512}$")
    tcpflags1: List[RulesRuleTcpflags1Enum] = Field(default_factory=list)
    tcpflags2: List[RulesRuleTcpflags2Enum] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list, description="Related category not found.")
    sched: Optional[str] = None
    tos: Optional[str] = None
    shaper1: Optional[str] = Field(default=None, description="Related pipe or queue not found.")
    shaper2: Optional[str] = Field(default=None, description="Related pipe or queue not found.")
    description: Optional[str] = None

