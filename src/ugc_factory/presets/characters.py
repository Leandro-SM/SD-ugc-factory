PERSONAS = {
 # Mulheres  
    "hanna": (
        "24 year old brazilian woman, long brown wavy hair, "
        "warm brown eyes, natural minimal makeup, athletic slim build, "
        "confident neutral expression"
    ),
    "ana": (
        "22 year old brazilian woman, short dark brown bob cut hair, "
        "warm brown eyes, freckles across nose and cheeks, "
        "no makeup natural skin, slim petite build, soft gentle expression"
    ),
    "sofia": (
        "27 year old brazilian woman, long blonde wavy hair tied in ponytail, "
        "green eyes, tanned skin, no makeup natural look, "
        "athletic fit toned build, energetic expression"
    ),
    "iris": (
        "35 year old professional woman, sleek shoulder-length black hair, "
        "dark brown almond-shaped eyes, defined cheekbones, "
        "subtle makeup, tall slim build, composed confident expression"
    ),
    "elena": (
        "45 year old woman, graceful shoulder-length silver gray hair, "
        "warm hazel eyes, light wrinkles around eyes, natural makeup, "
        "elegant slim build, sophisticated warm expression"
    ),
    "helena": (
        "65 year old active senior woman, short white hair, "
        "blue eyes, friendly smile lines, no makeup, "
        "slim healthy build, warm joyful expression"
    ),

 # Homens
    "mike": (
        "28 year old brazilian man, short dark brown hair, "
        "brown eyes, light stubble beard, athletic muscular build, "
        "casual confident expression"
    ),
    "miguel": (
        "22 year old brazilian man, curly dark hair, "
        "brown eyes, clean shaven, slim build, "
        "youthful student vibe, casual friendly expression"
    ),
    "carlos": (
        "35 year old man, short salt-and-pepper hair, "
        "brown eyes, well-groomed beard, fit athletic build, "
        "professional composed expression"
    ),
    "roberto": (
        "50 year old man, short gray hair receding hairline, "
        "brown eyes, clean shaven, average build, "
        "kind mature warm expression"
    ),
    "antonio": (
        "60 year old man, gray hair and full gray beard, glasses, "
        "dark eyes, slim build, intellectual scholarly vibe, "
        "thoughtful expression"
    ),
    "nathan": (
        "19 year old college student, messy brown hair, "
        "hazel eyes, clean shaven, slim build, "
        "energetic relaxed expression, casual streetwear vibe"
    ),
}

DEFAULT_PERSONA = "hanna"


def build_character(persona_key: str) -> str:
    return PERSONAS.get(persona_key, PERSONAS[DEFAULT_PERSONA])