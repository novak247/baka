import sys
import time
from pathlib import Path
from mistral_inference.transformer import Transformer
from mistral_inference.generate import generate
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest

# Nastavte cestu ke složce modelu; upravte podle potřeby.
mistral_models_path = Path.home().joinpath('mistral_models', '7B-Instruct-v0.3')

# Zkontrolujte, zda existuje soubor tokenizéru.
if not (mistral_models_path / "tokenizer.model.v3").exists():
    print("Model files not found. Please download them using snapshot_download as per the instructions.")
    sys.exit(1)



# Načtení tokenizéru a modelu z lokální složky.
tokenizer = MistralTokenizer.from_file(f"{mistral_models_path}/tokenizer.model.v3")
model = Transformer.from_folder(mistral_models_path, device="cuda")


# Definujte pevnou část promptu (instrukce pro robotického AI barmana v češtině).
prompt_header = """
Jsi RobBarman, robotický AI barman. Tvojí úlohou je interpretovat přirozený jazyk zákazníkového požadavku na drink a převést jej do série atomických operací potřebných k jeho realizaci. Následující atomické operace máš k dispozici:

1. "rozpoznat_napoj": Urči typ požadovaného nápoje.
   - Parametry: "napoj" (např. "pivo", "koktejl", "whiskey", apod.)

2. "zkontrolovat_suroviny": Zkontroluj, zda jsou dostupné potřebné suroviny.
   - Parametry: "suroviny" (seznam surovin potřebných pro přípravu nápoje)

3. "pripravit_napoj": Připrav drink smícháním surovin.
   - Parametry: "metoda" (např. "míchat", "protřepat", "míchat pomalu"), "suroviny" (seznam surovin), "množství" (volitelně, podrobnosti o dávkování)

4. "podat_napoj": Podávej nápoj zákazníkovi.
   - Parametry: "nádoba" (např. "sklenice", "hrnek"), "ozdoba" (pokud je potřeba)

Nevyhazuj žádný další text nebo vysvětlení – výstup musí být pouze validní JSON.

Nyní, na základě následujícího zákaznického požadavku, vygeneruj odpovídající JSON.
"""
# Read a single line customer request from the terminal.
user_request = input("Zadej zákaznický požadavek: ")

# Combine the fixed prompt header with the user's request.
final_prompt = prompt_header.strip() + "\n" + user_request.strip()

# Sestavte ChatCompletionRequest s kombinovaným promptem.
completion_request = ChatCompletionRequest(messages=[UserMessage(content=final_prompt)])

# Zakódujte chat completion request do tokenů.
encoded_tokens = tokenizer.encode_chat_completion(completion_request).tokens

# Vygenerujte výstupní tokeny (můžete upravit max_tokens, teplotu atd.).
out_tokens, _ = generate(
    [encoded_tokens],
    model,
    max_tokens=1000,
    temperature=0.0,
    eos_id=tokenizer.instruct_tokenizer.tokenizer.eos_id
)

# Dekódujte vygenerované tokeny do textu.
result = tokenizer.instruct_tokenizer.tokenizer.decode(out_tokens[0])
print("\nGenerated Output:")
print(result)
