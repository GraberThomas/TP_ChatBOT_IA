import os
from typing import cast
from openai.types.chat import ChatCompletionMessageParam
from main import ask_llm, get_available_models

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("=== Chatbot Groq CLI ===")
    
    # 1. Sélection du modèle
    try:
        models = get_available_models()
    except Exception as e:
        print(f"Erreur lors de la récupération des modèles : {e}")
        return

    print("\nModèles disponibles :")
    for i, model in enumerate(models):
        print(f"{i + 1}. {model}")
    
    choice = input("\nChoisissez un numéro de modèle (ou Entrée pour le premier) : ")
    index = int(choice) - 1 if choice.isdigit() and 0 < int(choice) <= len(models) else 0
    selected_model = models[index]
    
    print(f"\n✅ Modèle sélectionné : {selected_model}")
    print("Tapez 'exit' ou 'quit' pour quitter, ou 'clear' pour vider la mémoire.\n")

    # 2. Initialisation de la mémoire
    messages = [
        {"role": "assistant", "content": "Salut ! Comment puis-je t'aider aujourd'hui ?"}
    ]
    print(f"Assistant: {messages[0]['content']}")

    # 3. Boucle d'interaction
    while True:
        user_input = input("\nVous: ").strip()

        # Commandes spéciales
        if user_input.lower() in ["exit", "quit"]:
            print("Au revoir !")
            break
        
        if user_input.lower() == "clear":
            messages = [{"role": "assistant", "content": "Mémoire vidée. Que puis-je faire pour vous ?"}]
            clear_screen()
            print("=== Mémoire réinitialisée ===")
            print(f"Assistant: {messages[0]['content']}")
            continue

        if not user_input:
            continue

        # Ajouter le message utilisateur à l'historique
        messages.append({"role": "user", "content": user_input})

        print("### Assistant: ", end="", flush=True)
        
        try:
            # Appel au LLM (on passe tout l'historique pour la mémoire)
            response_text = ask_llm(
                messages=cast(list[ChatCompletionMessageParam], messages),
                model=selected_model
            )
            
            print(response_text)

            # Ajouter la réponse de l'assistant à l'historique
            messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            print(f"\nErreur : {e}")

if __name__ == "__main__":
    main()