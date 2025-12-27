import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
def get_api_key():
    return os.getenv("ANTHROPIC_API_KEY")


def get_beta_code():
    return os.getenv("BETA_ACCESS_CODE", "THAMES_CLUB_VIP")

# --- PROPRIETARY LOGIC ---
PERSONAS = {
    "menuGenerator": "You are a James Beard Award-winning chef who built your reputation on seasonal, ingredient-driven menus at a celebrated 40-seat restaurant. You're known for menus that tell a story—each course building on the last, flavors that echo and contrast, never a wasted element.",
    "recipeBuilder": "You are a Culinary Institute of America instructor who has trained thousands of home cooks. Your recipes are precise but approachable—exact measurements, clear technique explanations, and the 'why' behind each step.",
    "shoppingList": "You are a food writer for Bon Appétit who has organized hundreds of shopping lists. You group by store section, consolidate duplicates intelligently, and note substitutions.",
    "prepTimeline": "You are an executive chef who runs a flawless brigade kitchen. Everything is backward-scheduled from service time. Every task has a duration and a checkpoint.",
    "winePairings": "You are a Master Sommelier who trained at The French Laundry. You know when to suggest the ambitious pairing and when to play it safe.",
    "spirits": "You are the head bartender at a celebrated speakeasy known for balanced, crowd-pleasing punches and sophisticated cocktails.",
    "tableSettings": "You are an event designer whose work appears in Architectural Digest. You understand scale, proportion, sight lines, and candle placement.",
    "plating": "You are a culinary artist trained in kaiseki and modern French technique. Every plate is a composition—negative space matters, height matters, sauce placement matters.",
    "photographer": "You are a commercial food photographer who has shot for Gourmet and Food & Wine. You know that the magic is in the details—steam, condensation, the glisten of olive oil."
}

def call_claude(prompt):
    api_key = get_api_key()
    if not api_key:
        raise ValueError(
            "Missing ANTHROPIC_API_KEY. Set it in .env (recommended) or your environment and restart the app."
        )
        
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-5-sonnet-20240620", 
        "max_tokens": 8192,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=90,
        )
        response.raise_for_status()
        result = response.json()
        return result['content'][0]['text']
    except Exception as e:
        print(f"API Error: {e}")
        raise e

def extract_json(response_text):
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found in response")
        return json.loads(response_text[start:end])
    except Exception as e:
        print(f"JSON Parse Error. Raw text: {response_text[:100]}...")
        raise e

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/verify', methods=['POST'])
def verify_access():
    code = request.json.get('code', '')
    if code == get_beta_code():
        return jsonify({"valid": True})
    return jsonify({"valid": False}), 401

@app.route('/api/generate-menu', methods=['POST'])
def generate_menu():
    if request.json.get('accessCode') != get_beta_code():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json.get('data')
    
    # Build Prompt
    cat = data.get('menuCategory')
    details = data.get('categoryDetails', {})
    category_context = "Create balanced, impressive dinner party menus."
    
    if cat == 'tasting': category_context = 'Create elegant chef\'s tasting menus with refined pairings.'
    elif cat == 'regional': category_context = f"Create authentic {details.get('region', 'local')} regional American menus."
    elif cat == 'seasonal': category_context = 'Create seasonal, farm-to-table menus with peak freshness ingredients.'
    
    prompt = f"""{PERSONAS['menuGenerator']}

A host has asked you to design dinner party menus.
EVENT: {data.get('eventTitle', 'Dinner Party')}
GUESTS: {data.get('guests', 6)}
DIRECTION: {category_context}

PREFERENCES:
- Food Budget: {data.get('foodBudget')}
- Wine Budget: {data.get('wineBudget')}
- They love: {', '.join(data.get('likes', []))}
- They avoid: {', '.join(data.get('dislikes', []))}
- Dietary restrictions: {', '.join(data.get('restrictions', []))}
- Cuisine preference: {data.get('cuisine')}
- Skill: {data.get('skillLevel')}

Design 5 distinct menus. Each should tell a story.
RESPOND WITH ONLY VALID JSON:
{{
  "menus": [
    {{
      "name": "Menu Name",
      "description": "2-3 sentences on the story this menu tells",
      "courses": {{
        "amuse": {{"name": "Dish Name", "description": "Brief description"}},
        "first": {{"name": "Dish Name", "description": "Brief description"}},
        "second": {{"name": "Dish Name", "description": "Brief description"}},
        "main": {{"name": "Dish Name", "description": "Brief description"}},
        "dessert": {{"name": "Dish Name", "description": "Brief description"}}
      }},
      "wine": "Overall pairing philosophy",
      "estimatedFoodCost": "$XXX"
    }}
  ]
}}"""

    try:
        raw_response = call_claude(prompt)
        return jsonify(extract_json(raw_response))
    except ValueError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-cookbook', methods=['POST'])
def generate_cookbook():
    if request.json.get('accessCode') != get_beta_code():
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json.get('data')
    menu = data.get('menu')
    guests = data.get('guests')
    
    # "RECIPES FIRST" Logic
    prompt = f"""You are assembling a complete dinner party cookbook.
    
    CRITICAL INSTRUCTION: You must generate the detailed RECIPES first. 
    Then, create the SHOPPING LIST and PREP TIMELINE based *strictly* on those specific recipes.
    NEVER use generic terms like "Fish" or "Meat" or "Vegetables". 
    ALWAYS use specific amounts and items (e.g., "6x 6oz Halibut Fillets", "2 lbs Baby Carrots").
    
    EVENT: {data.get('eventTitle')}
    GUESTS: {guests}
    SKILL LEVEL: {data.get('skillLevel')}
    
    SELECTED MENU: {menu.get('name')}
    
    COURSES:
    - Amuse: {menu['courses']['amuse']['name']}
    - First: {menu['courses']['first']['name']}
    - Second: {menu['courses']['second']['name']}
    - Main: {menu['courses']['main']['name']}
    - Dessert: {menu['courses']['dessert']['name']}
    
    RESPOND WITH ONLY VALID JSON matching this structure. 
    (Note: 'recipes' must be generated before 'shopping' to ensure accuracy).
    
    {{
      "title": "{data.get('eventTitle')} Cookbook",
      
      "recipes": {{
        "_persona": "{PERSONAS['recipeBuilder']}",
        "courses": [
          {{
            "course": "Amuse/First/Main/etc", 
            "dish": "Specific Dish Name", 
            "yield": "{guests} servings",
            "prepTime": "XX min", 
            "cookTime": "XX min",
            "ingredients": [
                {{"item": "Specific Ingredient", "amount": "Exact Qty", "prep": "prep note"}}
            ],
            "instructions": ["Step 1", "Step 2"],
            "chefNotes": "Tips"
          }}
        ]
      }},

      "shopping": {{
        "_persona": "{PERSONAS['shoppingList']}",
        "_instruction": "Compile strictly from 'recipes' section. Consolidate amounts.",
        "proteins": [{{"item": "Specific Item", "quantity": "Total Needed", "notes": "notes"}}],
        "seafood": [], "dairy": [], "produce": [], "pantry": [], "specialty": []
      }},
      
      "dayBefore": {{
        "_persona": "{PERSONAS['prepTimeline']}",
        "_instruction": "Look at 'recipes' above. Identify steps that can be done 24h ahead.",
        "tasks": [{{"time": "Morning", "task": "Specific Task", "duration": "1h", "instructions": [], "storage": "method", "checkpoint": "verification"}}]
      }},
      
      "dayOf": {{
        "_persona": "Executive Chef",
        "serviceTime": "7:00 PM",
        "timeline": [{{"time": "3:00 PM", "task": "Specific Task", "duration": "30m", "details": [], "checkpoint": "verification"}}]
      }},

      "wines": {{
        "_persona": "{PERSONAS['winePairings']}",
        "aperitif": [{{"name": "Bottle", "description": "Why", "price": "$XX"}}],
        "dinner": [{{"name": "Bottle", "description": "Why", "price": "$XX"}}],
        "dessert": [{{"name": "Bottle", "description": "Why", "price": "$XX"}}]
      }},
      
      "cocktail": {{
        "_persona": "{PERSONAS['spirits']}",
        "name": "Cocktail Name", "description": "Desc",
        "ingredients": ["list"], "instructions": "text",
        "batchFor{guests}": "Batch instructions"
      }},
      
      "tableSetting": {{
        "_persona": "{PERSONAS['tableSettings']}",
        "mood": "text", "dimensions": "text",
        "placeSetting": {{"left": [], "right": [], "above": [], "glasses": []}},
        "centerpiece": "text", "lighting": "text", "linens": "text", "proTip": "text"
      }},
      
      "plating": {{
        "_persona": "{PERSONAS['plating']}",
        "courses": [
          {{
            "course": "Course", "vessel": "text", "composition": "text", 
            "sauce": "text", "garnish": "text", "temperature": "text", "principle": "text"
          }}
        ]
      }},
      
      "imagePrompts": {{
        "_persona": "{PERSONAS['photographer']}",
        "styleGuide": "Consistent visual style",
        "tablescape": "Prompt", "amuse": "Prompt", "first": "Prompt", 
        "second": "Prompt", "main": "Prompt", "dessert": "Prompt"
      }},
      
      "finalChecklist": {{
        "tableAndAmbiance": [], "kitchen": [], "drinks": [], "host": []
      }}
    }}"""
    
    try:
        raw_response = call_claude(prompt)
        return jsonify(extract_json(raw_response))
    except ValueError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=host, debug=debug, port=port)