import webbrowser

# Récupère le navigateur par défaut de l'utilisateur
browser = webbrowser.get()

def search_term(mot_cle):
    # Ouvre le navigateur par défaut avec le mot clé de recherche
    #Google
    #&udm
    browser.open(f"https://www.google.com/search?q={mot_cle}&udm=14")
    #Bing
    browser.open(f"https://www.bing.com/search?q={mot_cle}")
    #Brave
    browser.open(f"https://search.brave.com/search?q={mot_cle}")

def ask_continue():
    while True:
        reponse = input("\nVoulez-vous faire une nouvelle recherche ? (o/n) : ").lower()
        if reponse in ['o', 'n']:
            return reponse == 'o'
        print("Veuillez répondre par 'o' pour oui ou 'n' pour non.")

# Boucle principale
while True:
    # Demande un mot clé à l'utilisateur
    mot_cle = input("Entrez le terme de recherche : ")

    # On entoure le mot clé de recherche avec des guillemets pour une recherche plus précise  
    mot_cle = f'"{mot_cle}"'

    search_term(mot_cle)
    
    if not ask_continue():
        break

print("Au revoir !")




