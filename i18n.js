(function () {
    const storageKey = "synthesix-language";
    const supportedLanguages = ["en", "zh", "es", "fr", "pt", "de"];
    const settingsChannelName = "synthesix-settings";
    const textState = new WeakMap();
    const attributeState = new WeakMap();
    let observer = null;
    let applying = false;
    let settingsChannel = null;
    let pendingSettingsChange = null;

    const french = {
        "Search history": "Historique des recherches",
        "Search results": "Résultats de recherche",
        "Search": "Rechercher",
        "Filter results": "Filtrer les résultats",
        "Cancel search": "Annuler la recherche",
        "Search cancelled.": "Recherche annulée.",
        "A search is already running. Cancel it or wait for it to finish.": "Une recherche est déjà en cours. Annulez-la ou attendez qu'elle se termine.",
        "History": "Historique",
        "Settings": "Paramètres",
        "Language": "Langue",
        "Theme": "Thème",
        "System default": "Préférence système",
        "Light": "Clair",
        "Dark": "Sombre",
        "Close": "Fermer",
        "Save": "Enregistrer",
        "Cancel": "Annuler",
        "Open": "Ouvrir",
        "Title": "Titre",
        "Search engines": "Moteurs de recherche",
        "Site": "Site",
        "Exclude": "Exclure",
        "File": "Fichier",
        "Country": "Pays",
        "After": "Après",
        "Before": "Avant",
        "Results": "Résultats",
        "Add": "Ajouter",
        "Engine": "Moteur",
        "All engines": "Tous les moteurs",
        "Data": "Données",
        "Processing...": "Traitement en cours...",
        "Validated": "Validée",
        "Date": "Date",
        "Query": "Requête",
        "Status": "Statut",
    };

    const multilingual = {
        "Browser profiles": ["Profils navigateur","Perfiles del navegador","浏览器配置"],
        "Build your search": ["Construire la recherche","Preparar la búsqueda","构建搜索"],
        "Queries": ["Requêtes","Consultas","查询"],
        "One query per line": ["Une requête par ligne","Una consulta por línea","每行一个查询"],
        "Automatic exact-phrase dorks": ["Dorks automatiques en phrase exacte","Dorks automáticos de frase exacta","自动精确短语搜索"],
        "Dork filters": ["Filtres de dork","Filtros de dork","高级搜索筛选"],
        "File type": ["Type de fichier","Tipo de archivo","文件类型"],
        "Title contains": ["Le titre contient","El título contiene","标题包含"],
        "URL contains": ["L’URL contient","La URL contiene","网址包含"],
        "Page contains": ["La page contient","La página contiene","页面包含"],
        "Country code": ["Code pays","Código de país","国家代码"],
        "Results per engine": ["Résultats par moteur","Resultados por motor","每个引擎的结果数"],
        "Queries are merged into one deduplicated result list.": ["Les requêtes alimentent une seule liste de résultats sans doublons.","Las consultas se combinan en una lista sin duplicados.","查询合并为一个去重结果列表。"],
        "Open results with": ["Ouvrir les résultats avec","Abrir resultados con","使用以下配置打开结果"],
        "Neutral profile": ["Profil neutre","Perfil neutro","中立配置"],
        "All engines": ["Tous les moteurs","Todos los motores","所有引擎"],
        "engine requests completed": ["requêtes moteur terminées","solicitudes completadas","个引擎请求已完成"],
        "Search coverage": ["Couverture de la recherche","Cobertura de búsqueda","搜索覆盖情况"],
        "Relevance": ["Pertinence","Relevancia","相关性"],
        "Show more results": ["Afficher davantage de résultats","Mostrar más resultados","显示更多结果"],
        "No results match this filter.": ["Aucun résultat ne correspond à ce filtre.","Ningún resultado coincide con este filtro.","没有符合此筛选的结果。"],
        "Your next search starts here.": ["Votre prochaine recherche commence ici.","Tu próxima búsqueda empieza aquí.","从这里开始下一次搜索。"],
        "Searching selected engines...": ["Recherche sur les moteurs sélectionnés…","Buscando en los motores seleccionados…","正在搜索所选引擎…"],
        "Write your queries on the left, choose your engines, then search.": ["Saisissez vos requêtes à gauche, choisissez les moteurs, puis lancez la recherche.","Escribe las consultas a la izquierda, elige los motores y busca.","在左侧输入查询，选择引擎，然后开始搜索。"],
        "Each profile keeps its own website logins. Sign in once in its browser window.": ["Chaque profil conserve ses connexions aux sites. Connectez-vous une première fois dans sa fenêtre.","Cada perfil conserva sus sesiones. Inicia sesión una vez en su ventana.","每个配置保存各自的网站登录状态。请先在对应窗口登录一次。"],
        "Profile name": ["Nom du profil","Nombre del perfil","配置名称"],
        "Create profile": ["Créer un profil","Crear perfil","创建配置"],
        "Rename": ["Renommer","Renombrar","重命名"],
        "Open browser": ["Ouvrir le navigateur","Abrir navegador","打开浏览器"],
        "No browser profiles yet.": ["Aucun profil navigateur pour le moment.","Aún no hay perfiles.","尚无浏览器配置。"],
        "Profiles separate website sessions. They do not change your IP address.": ["Les profils séparent les sessions des sites. Ils ne changent pas votre adresse IP.","Los perfiles separan las sesiones. No cambian tu dirección IP.","配置隔离网站会话，但不会更改您的IP地址。"],
        "Reopen saved results or run the same queries again.": ["Retrouvez les résultats enregistrés ou relancez les mêmes requêtes.","Reabre resultados guardados o repite las consultas.","重新打开已保存的结果或再次运行相同查询。"],
        "results": ["résultats","resultados","个结果"],
        "Navigation": ["Navigation","Navegación","导航"],
        "Toggle theme": ["Changer de thème","Cambiar tema","切换主题"],
        "Starting Synthesix...": ["Démarrage de Synthesix…","Iniciando Synthesix…","正在启动Synthesix…"],
        "Ready to search.": ["Prêt à rechercher.","Listo para buscar.","可以开始搜索。"],
        "Application disconnected. Launch Synthesix to use this page.": ["Application déconnectée. Lancez Synthesix pour utiliser cette page.","Aplicación desconectada. Abre Synthesix para usar esta página.","应用已断开。请启动Synthesix以使用此页面。"],
        "Browser profile created.": ["Profil navigateur créé.","Perfil creado.","浏览器配置已创建。"],
        "Browser profile renamed.": ["Profil navigateur renommé.","Perfil renombrado.","浏览器配置已重命名。"],
        "Browser opened.": ["Navigateur ouvert.","Navegador abierto.","浏览器已打开。"],
        "Saved search restored.": ["Recherche enregistrée restaurée.","Búsqueda guardada restaurada.","已恢复保存的搜索。"],
        "Search completed.": ["Recherche terminée.","Búsqueda completada.","搜索已完成。"],
        "Some engines could not finish. Available results are shown.": ["Certains moteurs n’ont pas terminé. Les résultats disponibles sont affichés.","Algunos motores no terminaron. Se muestran los resultados disponibles.","部分引擎未完成。正在显示可用结果。"],
        "Search failed. Check engine coverage and retry.": ["Échec de la recherche. Consultez la couverture des moteurs et réessayez.","La búsqueda falló. Revisa la cobertura y reintenta.","搜索失败。请查看引擎覆盖情况后重试。"],
        "Results are available, but search history could not be saved.": ["Les résultats sont disponibles, mais l’historique n’a pas pu être enregistré.","Hay resultados, pero no se pudo guardar el historial.","结果可用，但无法保存搜索历史。"],
        "Enter between 1 and 20 queries, one per line.": ["Saisissez entre 1 et 20 requêtes, une par ligne.","Introduce entre 1 y 20 consultas, una por línea.","请输入1至20个查询，每行一个。"],
        "Each query must contain 1 to 500 characters.": ["Chaque requête doit contenir entre 1 et 500 caractères.","Cada consulta debe tener entre 1 y 500 caracteres.","每个查询必须包含1至500个字符。"],
        "Select at least one search engine.": ["Sélectionnez au moins un moteur de recherche.","Selecciona al menos un motor.","请至少选择一个搜索引擎。"],
        "Invalid search request.": ["Requête de recherche invalide.","Solicitud de búsqueda no válida.","搜索请求无效。"],
        "Invalid search options.": ["Options de recherche invalides.","Opciones de búsqueda no válidas.","搜索选项无效。"],
        "Invalid search filters.": ["Filtres de recherche invalides.","Filtros de búsqueda no válidos.","搜索筛选无效。"],
        "Unknown browser profile.": ["Profil navigateur inconnu.","Perfil desconocido.","未知浏览器配置。"],
        "Unknown saved search.": ["Recherche enregistrée inconnue.","Búsqueda guardada desconocida.","未知的已保存搜索。"],
        "Enter a profile name of 1 to 80 characters.": ["Saisissez un nom de profil de 1 à 80 caractères.","Introduce un nombre de 1 a 80 caracteres.","请输入1至80个字符的配置名称。"],
        "A profile with this name already exists.": ["Un profil porte déjà ce nom.","Ya existe un perfil con este nombre.","已存在同名配置。"],
        "Only valid HTTP or HTTPS addresses can be opened.": ["Seules les adresses HTTP ou HTTPS valides peuvent être ouvertes.","Solo se pueden abrir direcciones HTTP o HTTPS válidas.","只能打开有效的HTTP或HTTPS地址。"],
        "Invalid browser profile directory.": ["Répertoire de profil navigateur invalide.","Directorio de perfil no válido.","浏览器配置目录无效。"],
        "Browser executable not found.": ["Exécutable du navigateur introuvable.","No se encuentra el navegador.","未找到浏览器程序。"],
        "Action failed. Check the logs for details.": ["Échec de l’action. Consultez les journaux.","La acción falló. Consulta los registros.","操作失败。请查看日志。"],
        "ok": ["terminé","completado","完成"],
        "timeout": ["délai dépassé","tiempo agotado","超时"],
        "challenge": ["vérification requise","verificación necesaria","需要验证"],
        "error": ["erreur","error","错误"],
        "failed": ["en échec","con error","失败"],
        "engine requests": ["requêtes moteur","consultas a motores","次引擎请求"],
        "Filter by engine": ["Filtrer par moteur","Filtrar por motor","按引擎筛选"],
        "relevant results": ["résultats pertinents","resultados relevantes","相关结果"],
        "strong leads": ["pistes solides","pistas sólidas","有力线索"],
        "sources": ["sources","fuentes","来源"],
        "best score": ["meilleur score","mejor puntuación","最高得分"],
        "Sorted by relevance score.": ["Trié par score de pertinence.","Ordenado por puntuación de relevancia.","按相关度得分排序。"],
        "Score 8.0 and above.": ["Score de 8,0 et plus.","Puntuación de 8.0 o superior.","得分 8.0 及以上。"],
        "Search engines represented.": ["Moteurs de recherche représentés.","Motores de búsqueda representados.","涉及的搜索引擎。"],
        "Highest deterministic relevance.": ["Pertinence déterministe la plus élevée.","Mayor relevancia determinista.","最高的确定性相关度。"],
        "Found via": ["Trouvé via","Encontrado mediante","找到来源"],
        "navigate results": ["naviguer dans les résultats","navegar por los resultados","浏览结果"],
        "open": ["ouvrir","abrir","打开"],
        "No saved searches yet": ["Aucune recherche enregistrée pour l'instant","Aún no hay búsquedas guardadas","暂无已保存的搜索"],
        "Run a search from the home page to build your history.": ["Lancez une recherche depuis la page d'accueil pour constituer votre historique.","Ejecuta una búsqueda desde la página de inicio para crear tu historial.","在主页发起搜索即可建立历史记录。"],
        "Search history": ["Historique des recherches","Historial de búsquedas","搜索历史"],
        "Search results": ["Résultats de recherche","Resultados de búsqueda","搜索结果"],
        "Search": ["Rechercher","Buscar","搜索"],
        "Filter results": ["Filtrer les résultats","Filtrar resultados","筛选结果"],
        "Cancel search": ["Annuler la recherche","Cancelar la búsqueda","取消搜索"],
        "Search cancelled.": ["Recherche annulée.","Búsqueda cancelada.","搜索已取消。"],
        "A search is already running. Cancel it or wait for it to finish.": ["Une recherche est déjà en cours. Annulez-la ou attendez qu'elle se termine.","Ya hay una búsqueda en curso. Cancélala o espera a que termine.","已有搜索正在进行。请取消或等待其完成。"],
        "History": ["Historique","Historial","历史"],
        "Settings": ["Paramètres","Configuración","设置"],
        "Language": ["Langue","Idioma","语言"],
        "Theme": ["Thème","Tema","主题"],
        "System default": ["Préférence système","Predeterminado del sistema","跟随系统"],
        "Light": ["Clair","Claro","浅色"],
        "Dark": ["Sombre","Oscuro","深色"],
        "Close": ["Fermer","Cerrar","关闭"],
        "Save": ["Enregistrer","Guardar","保存"],
        "Cancel": ["Annuler","Cancelar","取消"],
        "Processing...": ["Traitement en cours...","Procesando...","处理中..."],
        "Open": ["Ouvrir","Abrir","打开"],
        "Title": ["Titre","Título","标题"],
        "Search engines": ["Moteurs de recherche","Motores de búsqueda","搜索引擎"],
        "Site": ["Site","Sitio","站点"],
        "Exclude": ["Exclure","Excluir","排除"],
        "File": ["Fichier","Archivo","文件"],
        "Country": ["Pays","País","国家/地区"],
        "After": ["Après","Después","之后"],
        "Before": ["Avant","Antes","之前"],
        "Results": ["Résultats","Resultados","结果"],
        "Add": ["Ajouter","Añadir","添加"],
        "Engine": ["Moteur","Motor","引擎"],
        "All engines": ["Tous les moteurs","Todos los motores","所有引擎"],
        "Data": ["Données","Datos","数据"],
        "Validated": ["Validée","Validada","已验证"],
        "Date": ["Date","Fecha","日期"],
        "Query": ["Requête","Consulta","查询"],
        "Status": ["Statut","Estado","状态"],
        "Unknown": ["Inconnu","Desconocido","未知"],
        "URL": ["URL","URL","URL"],
        "Text": ["Texte","Texto","文本"],
        "Score component": ["Composante du score","Componente de puntuación","评分组成"],
        "Search Results for": ["Résultats de recherche pour","Resultados de búsqueda para","搜索结果"],
        "Total time": ["Temps total","Tiempo total","总用时"],
        "Created": ["Créé","Creado","创建时间"],
        "All": ["Tous","Todos","全部"],
        "Synthesix History": ["Historique Synthesix","Historial de Synthesix","Synthesix 历史"],
        "View results": ["Voir les résultats","Ver resultados","查看结果"],
        "Retry": ["Réessayer","Reintentar","重试"],
        "Exact query": ["Requête exacte","Consulta exacta","精确查询"],
        "No relevant results found": ["Aucun résultat pertinent trouvé","No se encontraron resultados relevantes","未找到相关结果"],
        "Score": ["Score","Puntuación","评分"],
        "Searches": ["Recherches","Búsquedas","搜索"],
        "Automatic": ["Automatique","Automático","自动"],
        "Custom": ["Personnalisé","Personalizado","自定义"],
        "Profile": ["Profil","Perfil","配置文件"],
        "Partial": ["Partiel","Parcial","部分"],
        "Error": ["Erreur","Error","错误"],
        "No": ["Non","No","否"],
        "not run": ["non exécuté","no ejecutado","未运行"],
        "timeout": ["expiration","tiempo de espera agotado","超时"],
        "challenge": ["blocage anti-robot","bloqueo antirrobot","反机器人验证"],
        "error": ["erreur","error","错误"],
        "This report action is invalid.": ["Cette action de rapport est invalide.","Esta acción del informe no es válida.","此报告操作无效。"],
        "Type": ["Type","Tipo","类型"],
    };

    const languageIndexes = {fr: 0, es: 1, zh: 2};

    const additionalTranslations = {
        "Browser profiles": ["Perfis do navegador","Browserprofile"],
        "Build your search": ["Preparar pesquisa","Suche vorbereiten"],
        "Queries": ["Consultas","Suchanfragen"],
        "One query per line": ["Uma consulta por linha","Eine Suchanfrage pro Zeile"],
        "Automatic exact-phrase dorks": ["Dorks automáticos de frase exata","Automatische Dorks mit exakter Wortfolge"],
        "Dork filters": ["Filtros de dork","Dork-Filter"],
        "File type": ["Tipo de ficheiro","Dateityp"],
        "Title contains": ["O título contém","Titel enthält"],
        "URL contains": ["O URL contém","URL enthält"],
        "Page contains": ["A página contém","Seite enthält"],
        "Country code": ["Código do país","Ländercode"],
        "Results per engine": ["Resultados por motor","Ergebnisse pro Suchmaschine"],
        "Queries are merged into one deduplicated result list.": ["As consultas são reunidas numa lista sem duplicados.","Die Suchanfragen werden zu einer Ergebnisliste ohne Duplikate zusammengeführt."],
        "Open results with": ["Abrir resultados com","Ergebnisse öffnen mit"],
        "Neutral profile": ["Perfil neutro","Neutrales Profil"],
        "All engines": ["Todos os motores","Alle Suchmaschinen"],
        "engine requests completed": ["pedidos concluídos","Suchmaschinenanfragen abgeschlossen"],
        "Search coverage": ["Cobertura da pesquisa","Suchabdeckung"],
        "Relevance": ["Relevância","Relevanz"],
        "Show more results": ["Mostrar mais resultados","Weitere Ergebnisse anzeigen"],
        "No results match this filter.": ["Nenhum resultado corresponde a este filtro.","Keine Ergebnisse entsprechen diesem Filter."],
        "Your next search starts here.": ["A próxima pesquisa começa aqui.","Hier beginnt Ihre nächste Suche."],
        "Searching selected engines...": ["A pesquisar nos motores selecionados…","Ausgewählte Suchmaschinen werden durchsucht…"],
        "Write your queries on the left, choose your engines, then search.": ["Escreva as consultas à esquerda, escolha os motores e pesquise.","Geben Sie links Suchanfragen ein, wählen Sie die Suchmaschinen und starten Sie die Suche."],
        "Each profile keeps its own website logins. Sign in once in its browser window.": ["Cada perfil guarda as suas sessões. Inicie sessão uma vez na respetiva janela.","Jedes Profil behält seine Website-Anmeldungen. Melden Sie sich einmal im zugehörigen Fenster an."],
        "Profile name": ["Nome do perfil","Profilname"],
        "Create profile": ["Criar perfil","Profil erstellen"],
        "Rename": ["Mudar nome","Umbenennen"],
        "Open browser": ["Abrir navegador","Browser öffnen"],
        "No browser profiles yet.": ["Ainda não existem perfis.","Noch keine Browserprofile vorhanden."],
        "Profiles separate website sessions. They do not change your IP address.": ["Os perfis separam as sessões. Não alteram o seu endereço IP.","Profile trennen Website-Sitzungen. Sie ändern Ihre IP-Adresse nicht."],
        "Reopen saved results or run the same queries again.": ["Reabra os resultados guardados ou repita as consultas.","Öffnen Sie gespeicherte Ergebnisse oder führen Sie dieselben Suchanfragen erneut aus."],
        "results": ["resultados","Ergebnisse"],
        "Navigation": ["Navegação","Navigation"],
        "Toggle theme": ["Mudar tema","Design wechseln"],
        "Starting Synthesix...": ["A iniciar Synthesix…","Synthesix wird gestartet…"],
        "Ready to search.": ["Pronto para pesquisar.","Bereit für die Suche."],
        "Application disconnected. Launch Synthesix to use this page.": ["Aplicação desligada. Abra o Synthesix para usar esta página.","Anwendung getrennt. Starten Sie Synthesix, um diese Seite zu verwenden."],
        "Browser profile created.": ["Perfil criado.","Browserprofil erstellt."],
        "Browser profile renamed.": ["Nome do perfil alterado.","Browserprofil umbenannt."],
        "Browser opened.": ["Navegador aberto.","Browser geöffnet."],
        "Saved search restored.": ["Pesquisa guardada restaurada.","Gespeicherte Suche wiederhergestellt."],
        "Search completed.": ["Pesquisa concluída.","Suche abgeschlossen."],
        "Some engines could not finish. Available results are shown.": ["Alguns motores não terminaram. Os resultados disponíveis são apresentados.","Einige Suchmaschinen konnten nicht abschließen. Verfügbare Ergebnisse werden angezeigt."],
        "Search failed. Check engine coverage and retry.": ["A pesquisa falhou. Verifique a cobertura e tente novamente.","Suche fehlgeschlagen. Prüfen Sie die Suchabdeckung und versuchen Sie es erneut."],
        "Results are available, but search history could not be saved.": ["Os resultados estão disponíveis, mas não foi possível guardar o histórico.","Ergebnisse sind verfügbar, aber der Suchverlauf konnte nicht gespeichert werden."],
        "Enter between 1 and 20 queries, one per line.": ["Introduza entre 1 e 20 consultas, uma por linha.","Geben Sie 1 bis 20 Suchanfragen ein, eine pro Zeile."],
        "Each query must contain 1 to 500 characters.": ["Cada consulta deve ter entre 1 e 500 caracteres.","Jede Suchanfrage muss 1 bis 500 Zeichen enthalten."],
        "Select at least one search engine.": ["Selecione pelo menos um motor.","Wählen Sie mindestens eine Suchmaschine."],
        "Invalid search request.": ["Pedido de pesquisa inválido.","Ungültige Suchanfrage."],
        "Invalid search options.": ["Opções de pesquisa inválidas.","Ungültige Suchoptionen."],
        "Invalid search filters.": ["Filtros de pesquisa inválidos.","Ungültige Suchfilter."],
        "Unknown browser profile.": ["Perfil desconhecido.","Unbekanntes Browserprofil."],
        "Unknown saved search.": ["Pesquisa guardada desconhecida.","Unbekannte gespeicherte Suche."],
        "Enter a profile name of 1 to 80 characters.": ["Introduza um nome de perfil com 1 a 80 caracteres.","Geben Sie einen Profilnamen mit 1 bis 80 Zeichen ein."],
        "A profile with this name already exists.": ["Já existe um perfil com este nome.","Ein Profil mit diesem Namen existiert bereits."],
        "Only valid HTTP or HTTPS addresses can be opened.": ["Só podem ser abertos endereços HTTP ou HTTPS válidos.","Nur gültige HTTP- oder HTTPS-Adressen können geöffnet werden."],
        "Invalid browser profile directory.": ["Diretório de perfil inválido.","Ungültiges Browserprofilverzeichnis."],
        "Browser executable not found.": ["Executável do navegador não encontrado.","Browserprogramm nicht gefunden."],
        "Action failed. Check the logs for details.": ["A ação falhou. Consulte os registos.","Aktion fehlgeschlagen. Prüfen Sie die Protokolle."],
        "ok": ["concluído","abgeschlossen"],
        "timeout": ["tempo excedido","Zeitüberschreitung"],
        "challenge": ["verificação necessária","Bestätigung erforderlich"],
        "error": ["erro","Fehler"],
        "failed": ["com falha","fehlgeschlagen"],
        "engine requests": ["consultas a motores","Suchmaschinenanfragen"],
        "Filter by engine": ["Filtrar por motor","Nach Suchmaschine filtern"],
        "relevant results": ["resultados relevantes", "relevante Treffer"],
        "strong leads": ["pistas sólidas", "starke Hinweise"],
        "sources": ["fontes", "Quellen"],
        "best score": ["melhor pontuação", "bester Score"],
        "Sorted by relevance score.": ["Ordenado por pontuação de relevância.", "Nach Relevanz-Score sortiert."],
        "Score 8.0 and above.": ["Pontuação de 8,0 ou superior.", "Score 8,0 und höher."],
        "Search engines represented.": ["Motores de pesquisa representados.", "Vertretene Suchmaschinen."],
        "Highest deterministic relevance.": ["Maior relevância determinística.", "Höchste deterministische Relevanz."],
        "Found via": ["Encontrado via", "Gefunden über"],
        "navigate results": ["navegar pelos resultados", "Ergebnisse durchblättern"],
        "open": ["abrir", "öffnen"],
        "No saved searches yet": ["Ainda não há pesquisas guardadas", "Noch keine gespeicherten Suchen"],
        "Run a search from the home page to build your history.": ["Faça uma pesquisa na página inicial para criar o seu histórico.", "Starten Sie eine Suche auf der Startseite, um Ihren Verlauf aufzubauen."],
        "Search history": ["Histórico de pesquisas", "Suchverlauf"],
        "Search results": ["Resultados da pesquisa", "Suchergebnisse"],
        "Search": ["Pesquisar", "Suchen"],
        "Filter results": ["Filtrar resultados", "Ergebnisse filtern"],
        "Cancel search": ["Cancelar a pesquisa", "Suche abbrechen"],
        "Search cancelled.": ["Pesquisa cancelada.", "Suche abgebrochen."],
        "A search is already running. Cancel it or wait for it to finish.": ["Já existe uma pesquisa em curso. Cancele-a ou aguarde que termine.", "Es läuft bereits eine Suche. Brechen Sie sie ab oder warten Sie, bis sie beendet ist."],
        "History": ["Histórico", "Verlauf"],
        "Settings": ["Definições", "Einstellungen"],
        "Language": ["Idioma", "Sprache"],
        "Theme": ["Tema", "Design"],
        "System default": ["Predefinição do sistema", "Systemeinstellung"],
        "Light": ["Claro", "Hell"],
        "Dark": ["Escuro", "Dunkel"],
        "Close": ["Fechar", "Schließen"],
        "Save": ["Guardar", "Speichern"],
        "Cancel": ["Cancelar", "Abbrechen"],
        "Processing...": ["A processar...", "Verarbeitung..."],
        "Open": ["Abrir", "Öffnen"],
        "Title": ["Título", "Titel"],
        "Search engines": ["Motores de pesquisa", "Suchmaschinen"],
        "Site": ["Site", "Website"],
        "Exclude": ["Excluir", "Ausschließen"],
        "File": ["Ficheiro", "Datei"],
        "Country": ["País", "Land"],
        "After": ["Depois", "Nach"],
        "Before": ["Antes", "Vor"],
        "Results": ["Resultados", "Ergebnisse"],
        "Add": ["Adicionar", "Hinzufügen"],
        "Engine": ["Motor", "Suchmaschine"],
        "All engines": ["Todos os motores", "Alle Suchmaschinen"],
        "Data": ["Dados", "Daten"],
        "Validated": ["Validada", "Validiert"],
        "Date": ["Data", "Datum"],
        "Query": ["Consulta", "Abfrage"],
        "Status": ["Estado", "Status"],
        "Unknown": ["Desconhecido", "Unbekannt"],
        "URL": ["URL", "URL"],
        "Text": ["Texto", "Text"],
        "Score component": ["Componente da pontuação", "Bewertungskomponente"],
        "Search Results for": ["Resultados da pesquisa para", "Suchergebnisse für"],
        "Total time": ["Tempo total", "Gesamtzeit"],
        "Created": ["Criado", "Erstellt"],
        "All": ["Todos", "Alle"],
        "Synthesix History": ["Histórico do Synthesix", "Synthesix-Verlauf"],
        "View results": ["Ver resultados", "Ergebnisse anzeigen"],
        "Retry": ["Tentar novamente", "Erneut versuchen"],
        "Exact query": ["Consulta exata", "Exakte Abfrage"],
        "No relevant results found": ["Nenhum resultado relevante encontrado", "Keine relevanten Ergebnisse gefunden"],
        "Score": ["Pontuação", "Bewertung"],
        "Searches": ["Pesquisas", "Suchen"],
        "Automatic": ["Automático", "Automatisch"],
        "Custom": ["Personalizado", "Benutzerdefiniert"],
        "Profile": ["Perfil", "Profil"],
        "Partial": ["Parcial", "Teilweise"],
        "Error": ["Erro", "Fehler"],
        "No": ["Não", "Nein"],
        "not run": ["não executado", "nicht ausgeführt"],
        "timeout": ["tempo limite", "Zeitüberschreitung"],
        "challenge": ["bloqueio antirrobô", "Anti-Bot-Prüfung"],
        "error": ["erro", "Fehler"],
        "This report action is invalid.": ["Esta ação do relatório é inválida.", "Diese Berichtsaktion ist ungültig."],
        "Type": ["Tipo", "Typ"],
    };

    const additionalLanguageIndexes = {pt: 0, de: 1};

    const attributeNames = ["placeholder", "title", "aria-label"];

    function normalizeLanguage(value) {
        const language = String(value || "").trim().toLowerCase().split("-")[0];
        return supportedLanguages.includes(language) ? language : "en";
    }

    function detectedLanguage() {
        const candidates = Array.isArray(navigator.languages)
            ? navigator.languages
            : [navigator.language];
        for (const candidate of candidates) {
            const language = normalizeLanguage(candidate);
            if (language !== "en" || String(candidate || "").toLowerCase().startsWith("en")) {
                return language;
            }
        }
        return "en";
    }

    function storedLanguage() {
        try {
            const stored = window.localStorage.getItem(storageKey);
            return stored ? normalizeLanguage(stored) : null;
        } catch (_error) {
            return null;
        }
    }

    function currentLanguage() {
        return storedLanguage() || detectedLanguage();
    }

    function translatePattern(value, language) {
        if (language === "en") {
            return value;
        }
        const patternsByLanguage = {
            fr: [
                [/^(\d+) result\(s\)$/, "$1 résultat(s)"],
                [/^(\d+) results$/, "$1 résultats"],
                [/^(\d+) visible$/, "$1 visibles"],
                [/^Query coverage \((\d+) variants\)$/, "Couverture des requêtes ($1 variantes)"],
                [/^(\d+) saved searches$/, "$1 recherches enregistrées"],
                [/^(\d+) export\(s\)$/, "$1 export(s)"],
                [/^(\d+) nodes$/, "$1 nœuds"],
                [/^(\d+) links$/, "$1 liens"],
                [/^(\d+) assets$/, "$1 assets"],
                [/^(\d+) evidence capture\(s\)$/, "$1 capture(s) de preuve"],
                [/^(\d+) observation(?:\(s\)|s)?$/, "$1 observation(s)"],
                [/^(\d+) archive(?:\(s\)|s)?$/, "$1 archive(s)"],
                [/^(\d+) monitored$/, "$1 surveillée(s)"],
                [/^Total time: (.+) seconds$/, "Temps total : $1 secondes"],
                [/^Created: (.+)$/, "Créé : $1"],
                [/^Search Results for: (.+)$/, "Résultats de recherche pour : $1"],
                [/^At most (.+) additional variants can run\.$/, "Au maximum $1 variantes supplémentaires peuvent être exécutées."],
                [/^Archive the investigation \"(.+)\"\?$/, "Archiver l'enquête « $1 » ?"],
                [/^Delete the empty investigation \"(.+)\"\? Investigations containing searches must be archived\.$/, "Supprimer l'enquête vide « $1 » ? Les enquêtes contenant des recherches doivent être archivées."]
            ],
            es: [
                [/^(\d+) result\(s\)$/, "$1 resultado(s)"],
                [/^(\d+) results$/, "$1 resultados"],
                [/^(\d+) visible$/, "$1 visibles"],
                [/^Query coverage \((\d+) variants\)$/, "Cobertura de consultas ($1 variantes)"],
                [/^(\d+) saved searches$/, "$1 búsquedas guardadas"],
                [/^(\d+) export\(s\)$/, "$1 exportación(es)"],
                [/^(\d+) nodes$/, "$1 nodos"],
                [/^(\d+) links$/, "$1 enlaces"],
                [/^(\d+) assets$/, "$1 recursos"],
                [/^(\d+) evidence capture\(s\)$/, "$1 captura(s) de evidencia"],
                [/^(\d+) observation(?:\(s\)|s)?$/, "$1 observación(es)"],
                [/^(\d+) archive(?:\(s\)|s)?$/, "$1 archivo(s)"],
                [/^(\d+) monitored$/, "$1 monitorizada(s)"],
                [/^Total time: (.+) seconds$/, "Tiempo total: $1 segundos"],
                [/^Created: (.+)$/, "Creado: $1"],
                [/^Search Results for: (.+)$/, "Resultados de búsqueda para: $1"],
                [/^At most (.+) additional variants can run\.$/, "Como máximo pueden ejecutarse $1 variantes adicionales."],
                [/^Archive the investigation \"(.+)\"\?$/, "¿Archivar la investigación «$1»?"],
                [/^Delete the empty investigation \"(.+)\"\? Investigations containing searches must be archived\.$/, "¿Eliminar la investigación vacía «$1»? Las investigaciones con búsquedas deben archivarse."]
            ],
            zh: [
                [/^(\d+) result\(s\)$/, "$1 个结果"],
                [/^(\d+) results$/, "$1 个结果"],
                [/^(\d+) visible$/, "$1 个可见"],
                [/^Query coverage \((\d+) variants\)$/, "查询覆盖（$1 个变体）"],
                [/^(\d+) saved searches$/, "$1 条已保存搜索"],
                [/^(\d+) export\(s\)$/, "$1 个导出"],
                [/^(\d+) nodes$/, "$1 个节点"],
                [/^(\d+) links$/, "$1 条链接"],
                [/^(\d+) assets$/, "$1 个资源"],
                [/^(\d+) evidence capture\(s\)$/, "$1 个证据捕获"],
                [/^(\d+) observation(?:\(s\)|s)?$/, "$1 次观察"],
                [/^(\d+) archive(?:\(s\)|s)?$/, "$1 个归档"],
                [/^(\d+) monitored$/, "$1 个受监控页面"],
                [/^Total time: (.+) seconds$/, "总用时：$1 秒"],
                [/^Created: (.+)$/, "创建时间：$1"],
                [/^Search Results for: (.+)$/, "“$1”的搜索结果"],
                [/^At most (.+) additional variants can run\.$/, "最多可运行 $1 个其他变体。"],
                [/^Archive the investigation \"(.+)\"\?$/, "是否归档调查“$1”？"],
                [/^Delete the empty investigation \"(.+)\"\? Investigations containing searches must be archived\.$/, "是否删除空调查“$1”？包含搜索的调查必须归档。"]
            ],
            pt: [
                [/^(\d+) result\(s\)$/, "$1 resultado(s)"],
                [/^(\d+) results$/, "$1 resultados"],
                [/^(\d+) visible$/, "$1 visíveis"],
                [/^Query coverage \((\d+) variants\)$/, "Cobertura das consultas ($1 variantes)"],
                [/^(\d+) saved searches$/, "$1 pesquisas guardadas"],
                [/^(\d+) export\(s\)$/, "$1 exportação(ões)"],
                [/^(\d+) nodes$/, "$1 nós"],
                [/^(\d+) links$/, "$1 ligações"],
                [/^(\d+) assets$/, "$1 recursos"],
                [/^(\d+) evidence capture\(s\)$/, "$1 captura(s) de prova"],
                [/^(\d+) observation(?:\(s\)|s)?$/, "$1 observação(ões)"],
                [/^(\d+) archive(?:\(s\)|s)?$/, "$1 arquivo(s)"],
                [/^(\d+) monitored$/, "$1 monitorizada(s)"],
                [/^Total time: (.+) seconds$/, "Tempo total: $1 segundos"],
                [/^Created: (.+)$/, "Criado: $1"],
                [/^Search Results for: (.+)$/, "Resultados da pesquisa para: $1"],
                [/^At most (.+) additional variants can run\.$/, "Podem ser executadas, no máximo, $1 variantes adicionais."],
                [/^Archive the investigation \"(.+)\"\?$/, "Arquivar a investigação «$1»?"],
                [/^Delete the empty investigation \"(.+)\"\? Investigations containing searches must be archived\.$/, "Eliminar a investigação vazia «$1»? As investigações com pesquisas têm de ser arquivadas."]
            ],
            de: [
                [/^(\d+) result\(s\)$/, "$1 Ergebnis(se)"],
                [/^(\d+) results$/, "$1 Ergebnisse"],
                [/^(\d+) visible$/, "$1 sichtbar"],
                [/^Query coverage \((\d+) variants\)$/, "Abfrageabdeckung ($1 Varianten)"],
                [/^(\d+) saved searches$/, "$1 gespeicherte Suchen"],
                [/^(\d+) export\(s\)$/, "$1 Export(e)"],
                [/^(\d+) nodes$/, "$1 Knoten"],
                [/^(\d+) links$/, "$1 Verknüpfungen"],
                [/^(\d+) assets$/, "$1 Assets"],
                [/^(\d+) evidence capture\(s\)$/, "$1 Beweisaufnahme(n)"],
                [/^(\d+) observation(?:\(s\)|s)?$/, "$1 Beobachtung(en)"],
                [/^(\d+) archive(?:\(s\)|s)?$/, "$1 Archiv(e)"],
                [/^(\d+) monitored$/, "$1 überwachte Seite(n)"],
                [/^Total time: (.+) seconds$/, "Gesamtzeit: $1 Sekunden"],
                [/^Created: (.+)$/, "Erstellt: $1"],
                [/^Search Results for: (.+)$/, "Suchergebnisse für: $1"],
                [/^At most (.+) additional variants can run\.$/, "Es können höchstens $1 zusätzliche Varianten ausgeführt werden."],
                [/^Archive the investigation \"(.+)\"\?$/, "Ermittlung „$1“ archivieren?"],
                [/^Delete the empty investigation \"(.+)\"\? Investigations containing searches must be archived\.$/, "Leere Ermittlung „$1“ löschen? Ermittlungen mit Suchen müssen archiviert werden."]
            ]
        };
        const patterns = patternsByLanguage[language] || [];
        for (const [pattern, replacement] of patterns) {
            if (pattern.test(value)) {
                return value.replace(pattern, replacement);
            }
        }
        return value;
    }

    function t(value, language = currentLanguage()) {
        const text = String(value || "");
        if (language === "en") {
            return text;
        }
        const normalized = text.replace(/\s+/g, " ").trim();
        const additionalRow = additionalTranslations[normalized];
        if (
            additionalRow
            && additionalLanguageIndexes[language] !== undefined
        ) {
            return additionalRow[additionalLanguageIndexes[language]];
        }
        const row = multilingual[normalized];
        if (row && languageIndexes[language] !== undefined) {
            return row[languageIndexes[language]];
        }
        if (
            language === "fr"
            && Object.prototype.hasOwnProperty.call(french, normalized)
        ) {
            return french[normalized];
        }
        return translatePattern(normalized, language);
    }

    function translateTextNode(node, language) {
        if (!node.data.trim()) {
            return;
        }
        const previous = textState.get(node);
        let source = previous ? previous.source : node.data;
        if (previous && node.data !== previous.translated) {
            source = node.data;
        }
        const leading = source.match(/^\s*/)[0];
        const trailing = source.match(/\s*$/)[0];
        const core = source.trim();
        const translated = `${leading}${t(core, language)}${trailing}`;
        textState.set(node, { source, translated });
        if (node.data !== translated) {
            node.data = translated;
        }
    }

    function translateAttributes(element, language) {
        let states = attributeState.get(element);
        if (!states) {
            states = {};
            attributeState.set(element, states);
        }
        for (const name of attributeNames) {
            if (!element.hasAttribute(name)) {
                continue;
            }
            const current = element.getAttribute(name);
            const previous = states[name];
            const source = previous && current === previous.translated
                ? previous.source
                : current;
            const translated = t(source, language);
            states[name] = { source, translated };
            if (current !== translated) {
                element.setAttribute(name, translated);
            }
        }
    }

    function translateTree(root = document, language = currentLanguage()) {
        applying = true;
        document.documentElement.lang = language;
        document.documentElement.dir = "ltr";
        const walker = document.createTreeWalker(
            root,
            NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT
        );
        let node = root;
        do {
            if (node.nodeType === Node.TEXT_NODE) {
                const parent = node.parentElement;
                if (parent && !["SCRIPT", "STYLE", "PRE", "CODE"].includes(parent.tagName)) {
                    translateTextNode(node, language);
                }
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                translateAttributes(node, language);
            }
            node = walker.nextNode();
        } while (node);
        applying = false;
        document.dispatchEvent(
            new CustomEvent("synthesix:languagechange", {
                detail: { language }
            })
        );
    }

    function applyLanguage(language, persist = false) {
        const normalized = normalizeLanguage(language);
        if (persist) {
            try {
                window.localStorage.setItem(storageKey, normalized);
            } catch (_error) {
                // Keep the in-memory language even when storage is unavailable.
            }
        }
        translateTree(document, normalized);
        localizeCountryOptions(normalized);
        syncSettings();
        return normalized;
    }

    function broadcastSettings(settings) {
        pendingSettingsChange = {
            ...(pendingSettingsChange || {}),
            ...settings
        };
        settingsChannel?.postMessage(settings);
    }

    function consumeSettingsChange() {
        const settings = pendingSettingsChange;
        pendingSettingsChange = null;
        return settings;
    }

    function applySettings(settings) {
        const values = settings || {};
        if (values.language) {
            applyLanguage(values.language, true);
        }
        if (values.theme) {
            applyThemeSetting(values.theme, false);
        }
    }

    function setLanguage(language) {
        const normalized = applyLanguage(language, true);
        broadcastSettings({ language: normalized });
    }

    function settingsMarkup() {
        return `
            <dialog id="synthesix-settings-dialog" class="investigation-dialog settings-dialog">
                <form method="dialog" class="investigation-form">
                    <div class="dialog-header">
                        <h2>Settings</h2>
                        <button class="icon-button" type="submit" aria-label="Close" title="Close">&times;</button>
                    </div>
                    <div class="dialog-fields">
                        <label for="synthesix-language-select">
                            <span>Language</span>
                            <select id="synthesix-language-select">
                                <option value="en">English</option>
                                <option value="zh">中文（普通话）</option>
                                <option value="es">Español</option>
                                <option value="fr">Français</option>
                                <option value="pt">Português</option>
                                <option value="de">Deutsch</option>
                            </select>
                        </label>
                        <label for="synthesix-theme-select">
                            <span>Theme</span>
                            <select id="synthesix-theme-select">
                                <option value="system">System default</option>
                                <option value="light">Light</option>
                                <option value="dark">Dark</option>
                            </select>
                        </label>
                    </div>
                    <div class="dialog-actions">
                        <button class="primary-button" type="submit">Close</button>
                    </div>
                </form>
            </dialog>
        `;
    }

    function preferredThemeSetting() {
        try {
            return window.localStorage.getItem("synthesix-theme") || "system";
        } catch (_error) {
            return "system";
        }
    }

    function applyThemeSetting(value, broadcast = true) {
        if (value === "light" || value === "dark") {
            window.synthesixTheme?.setTheme(value);
        } else {
            try {
                window.localStorage.removeItem("synthesix-theme");
            } catch (_error) {
                // Apply the system theme even if storage is unavailable.
            }
            const systemTheme = window.matchMedia?.("(prefers-color-scheme: dark)").matches
                ? "dark"
                : "light";
            window.synthesixTheme?.applyTheme(systemTheme);
        }
        syncSettings();
        if (broadcast) {
            broadcastSettings({ theme: value });
        }
    }

    function syncSettings() {
        const languageSelect = document.getElementById("synthesix-language-select");
        const themeSelect = document.getElementById("synthesix-theme-select");
        if (languageSelect) {
            languageSelect.value = currentLanguage();
        }
        if (themeSelect) {
            themeSelect.value = preferredThemeSetting();
        }
    }

    function installSettings() {
        if (document.getElementById("synthesix-settings-dialog")) {
            return;
        }
        document.body.insertAdjacentHTML("beforeend", settingsMarkup());
        const dialog = document.getElementById("synthesix-settings-dialog");
        const languageSelect = document.getElementById("synthesix-language-select");
        const themeSelect = document.getElementById("synthesix-theme-select");
        languageSelect.addEventListener("change", () => {
            setLanguage(languageSelect.value);
        });
        themeSelect.addEventListener("change", () => {
            applyThemeSetting(themeSelect.value);
        });
        document.querySelectorAll(".top-actions").forEach((actions, index) => {
            if (index > 0 || actions.querySelector("[data-settings-button]")) {
                return;
            }
            const button = document.createElement("button");
            button.type = "button";
            button.className = "nav-link";
            button.dataset.settingsButton = "";
            button.textContent = "Settings";
            button.addEventListener("click", () => {
                syncSettings();
                dialog.showModal();
            });
            actions.appendChild(button);
        });
        syncSettings();
    }

    function localizeCountryOptions(language) {
        if (!window.Intl || typeof Intl.DisplayNames !== "function") {
            return;
        }
        const displayNames = new Intl.DisplayNames([language], { type: "region" });
        document.querySelectorAll("#country-options option").forEach((option) => {
            const region = String(option.textContent || "").trim().toUpperCase();
            if (/^[A-Z]{2}$/.test(region)) {
                option.label = displayNames.of(region) || option.value;
            }
        });
    }

    function installDialogTranslations() {
        const nativeAlert = window.alert.bind(window);
        const nativeConfirm = window.confirm.bind(window);
        window.alert = (message) => nativeAlert(t(message));
        window.confirm = (message) => nativeConfirm(t(message));
    }

    function installSettingsSynchronization() {
        if (typeof window.BroadcastChannel === "function") {
            try {
                settingsChannel = new BroadcastChannel(settingsChannelName);
                settingsChannel.addEventListener("message", (event) => {
                    applySettings(event.data);
                });
            } catch (_error) {
                settingsChannel = null;
            }
        }
        window.addEventListener("storage", (event) => {
            if (event.key === storageKey) {
                applyLanguage(event.newValue || detectedLanguage());
            } else if (event.key === "synthesix-theme") {
                applyThemeSetting(event.newValue || "system", false);
            }
        });
    }

    function init() {
        installSettings();
        installDialogTranslations();
        installSettingsSynchronization();
        translateTree(document, currentLanguage());
        localizeCountryOptions(currentLanguage());
        observer = new MutationObserver((mutations) => {
            if (applying) {
                return;
            }
            for (const mutation of mutations) {
                if (mutation.type === "characterData") {
                    translateTextNode(mutation.target, currentLanguage());
                } else if (mutation.type === "attributes") {
                    translateAttributes(mutation.target, currentLanguage());
                } else {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            translateTree(node, currentLanguage());
                        } else if (node.nodeType === Node.TEXT_NODE) {
                            translateTextNode(node, currentLanguage());
                        }
                    });
                }
            }
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true,
            attributes: true,
            attributeFilter: attributeNames
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init, { once: true });
    } else {
        init();
    }

    window.synthesixI18n = {
        applySettings,
        consumeSettingsChange,
        currentLanguage,
        detectedLanguage,
        setLanguage,
        t,
        translateTree
    };
})();
