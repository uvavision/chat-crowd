DOMAIN_2DSHAPE = '2Dshape'
USER = 'user'
AGENT = 'agent'
OTHER_ROLE = {AGENT: USER, USER: AGENT}
# painter -- agent / instructor -- user

INFORM = 'inform'
CONFIRM = 'confirm'
REJECT = 'reject'
REQUEST = 'request'  # instruct
SELF_CORRECTION = 'self-correction'
ASK_Q = 'ask-question'
END = 'end-conversation'
DAS = [INFORM, CONFIRM, REQUEST]
IS_VIABLE = 'is_viable'

ACT = 'act'

COLORS = ['red', 'green', 'blue']
SHAPES = ['square', 'circle', 'triangle']

MODE_FULL = 'full'
MODE_MIN = 'min'
MODES_REF = [MODE_MIN, MODE_FULL]

LOC_ABS = 'loc_abs'  # 'location_absolute'
LOC_REL = 'loc_rel'  #'location_relative'
MODES_LOC = [LOC_ABS, LOC_REL]

# SINGLE = 'single'
# MULTI = 'multi'
# PATTERN = 'pattern'
# MODES_STYLE = [SINGLE, PATTERN]
# PATTERN_STYLE = ['row', 'column']

# error type

# state of grid
STATE_EMPTY = 0
STATE_OCCU = 1
STATES = [STATE_EMPTY, STATE_OCCU]

STATUS_SUCCESSFUL = True
STATUS_FAILED = False

OBJ = 'obj'
OBJ_REF = 'obj_rel'
OBJ_PTTN = 'object_pattern'

COLOR = 'color'
SHAPE = 'shape'
ROW = 'row'
COL = 'col'
ID = 'id_'
FEATURES = 'features'
MESSAGE = 'message'

ADD = 'add'
DELETE = 'delete'
MOVE = 'move'
ACTIONS = [ADD, DELETE, MOVE]

GRID_SIZE = 5

DICT_NAME2LOC_ABS = {
    'top-left': (0, 0),
    'top-right': (0, GRID_SIZE - 1),
    'bottom-left': (GRID_SIZE - 1, 0),
    'bottom-right': (GRID_SIZE - 1, GRID_SIZE - 1),
    'center': (GRID_SIZE // 2, GRID_SIZE // 2),
    'top-middle': (0, GRID_SIZE // 2),
    'bottom-middle': (GRID_SIZE - 1, GRID_SIZE // 2),
    'left-middle': (GRID_SIZE // 2, 0),
    'right-middle': (GRID_SIZE // 2, GRID_SIZE - 1)
}

DICT_LOC_ABS2NAME = {v: k for k, v in DICT_NAME2LOC_ABS.items()}

DICT_LOC_DELTA2NAME = {
    (-1, 0): 'top-of',  # A is at top-of B  (A.row - B.row)
    (1, 0): 'bottom-of',
    (0, 1): 'right-of',
    (0, -1): 'left-of',
    (-1, -1): 'top-left-of',
    (-1, 1): 'top-right-of',
    (1, -1): 'bottom-left-of',
    (1, 1): 'bottom-right-of',
}

TMPL_ADD = ["Add one $obj.", "Now place a $obj."]

TMPL_DEL = ["Please remove the $obj from the canvas.", "Delete the $obj.", "Now get rid of the $obj."]

TMPL_MV = ["move the $obj to $loc_abs $loc_rel", "place the $obj to $loc_abs $loc_rel"]

TMPL_LOC_ABS = ["to/at $loc_abs of the canvas"]

TMPL_LOC_REL = ["to/at $loc_rel of the $obj_ref"]

TMPL_OBJ_REF = ["$color $shape at $loc_rel of the $loc_abs location of the canvas"]

TMPL_OBJ = ["$color $shape object ", "$color $shape one "]

# self correction is right after original utterance
TMPL_DA_SELF_CORRECTION_ADD = ["Wait, make the $k $v instead.", "Sorry, my mistake, the $k is $v."]

TMPL_DA_SELF_CORRECTION_ADD_MULTI = ["Wait, make the $k1 $v1 and $k2 $v2 instead.",
                                 "Sorry, my mistake, the $k1 is $v1 and the $k2 is $v2."]

TMPL_DA_SELF_CORRECTION_DELETE = ["My mistake, I meant the $v instead", "Oh, no, I meant the $v instead"]

TMPL_DA_CORRECTION = ["Wait, make the $k $v instead.", "Sorry, my mistake, the $k is $v."]

TMPL_DA_CONFIRM_AGENT = ["Done.", "Sure.", "OK!"]

TMPL_DA_CONFIRM_USER = ["Correct.", "Yes.", "Right."]

TMPL_DA_REJECT_USER = ["No.", "Can't do it.", "Not really."]

TMPL_DA_END_USER = ["#END"]

TMPL_DA_ASKQ_AGENT = ["Do you mean $obj at $loc_abs $loc_rel? ", "You want $obj at $loc_abs $loc_rel?"]

TMPL_DA_ASKQ_AGENT_ADD = ["Are you sure? There is already an object at $t_loc_abs $t_loc_rel. "]

TMPL_DA_ASKQ_AGENT_DELETE = ["Are you sure? There is no object at $t_loc_abs $t_loc_rel. "]

TEXT_EMPTY_GRID = ["There is no shape at that location.", "The position is empty."]

TEXT_OCCUPIED_GRID = ["There is already an object.", "The position is not empty."]

T_OBJ = 't_obj'
T_LOC_ABS = 't_loc_abs'
T_LOC_REL = 't_loc_rel'

SINGLE = 0
MULTIPLE = 1

VIABLE = True
NOT_VIABLE = False

DICT_TEMPLATES = {
    ADD: TMPL_ADD,
    DELETE: TMPL_DEL,
    MOVE: TMPL_MV,
    OBJ: TMPL_OBJ,
    OBJ_REF: TMPL_OBJ_REF,
    LOC_ABS: TMPL_LOC_ABS,
    LOC_REL: TMPL_LOC_REL,
    (CONFIRM, AGENT): TMPL_DA_CONFIRM_AGENT,
    (CONFIRM, USER): TMPL_DA_CONFIRM_USER,
    (REJECT, USER): TMPL_DA_REJECT_USER,
    (SELF_CORRECTION, USER, ADD, SINGLE): TMPL_DA_SELF_CORRECTION_ADD,
    (SELF_CORRECTION, USER, ADD, MULTIPLE): TMPL_DA_SELF_CORRECTION_ADD_MULTI,
    (SELF_CORRECTION, USER, DELETE, SINGLE): TMPL_DA_SELF_CORRECTION_DELETE,
    (SELF_CORRECTION, USER, DELETE, MULTIPLE): TMPL_DA_SELF_CORRECTION_DELETE,
    (ASK_Q, AGENT): TMPL_DA_ASKQ_AGENT,
    (ASK_Q, AGENT, ADD): TMPL_DA_ASKQ_AGENT_ADD,
    (ASK_Q, AGENT, DELETE): TMPL_DA_ASKQ_AGENT_DELETE,
    (END, USER): TMPL_DA_END_USER
}

D_ACTION_MAPPING = {
    (USER, REQUEST, VIABLE): [
        (AGENT, CONFIRM, VIABLE),
        (AGENT, ASK_Q, VIABLE)
    ],
    (USER, REQUEST, NOT_VIABLE): [
        (AGENT, ASK_Q, NOT_VIABLE)
    ],
    (AGENT, CONFIRM, VIABLE): [
        (USER, REQUEST, VIABLE)
    ],
    (USER, CONFIRM, VIABLE): [
        (AGENT, CONFIRM, VIABLE)
    ],
    (USER, SELF_CORRECTION, VIABLE): [
        (AGENT, CONFIRM, VIABLE),
        (AGENT, ASK_Q, VIABLE)
    ],
    (USER, SELF_CORRECTION, NOT_VIABLE): [
        (AGENT, CONFIRM, VIABLE),
    ],
    (AGENT, ASK_Q, VIABLE): [
        (USER, CONFIRM, VIABLE),
        # (USER, REJECT, VIABLE),
    ],
    (AGENT, ASK_Q, NOT_VIABLE): [
        # (USER, REJECT, VIABLE),
        (USER, SELF_CORRECTION, NOT_VIABLE)
    ],
    (USER, ASK_Q, VIABLE): [
        (AGENT, CONFIRM, VIABLE)
    ]
}