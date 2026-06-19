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
        "Multi-engine search": "Recherche multi-moteurs",
        "Investigation workspace": "Espace d'enquête",
        "Search history": "Historique des recherches",
        "Search results": "Résultats de recherche",
        "Local archive search": "Recherche dans l'archive locale",
        "Search, compare, synthesize.": "Rechercher, comparer, synthétiser.",
        "Search workspace": "Espace de recherche",
        "Search": "Rechercher",
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
        "Checking VPN": "Vérification du VPN",
        "VPN likely": "VPN probable",
        "VPN not detected": "VPN non détecté",
        "VPN unknown": "VPN inconnu",
        "Investigation": "Enquête",
        "Investigations": "Enquêtes",
        "No investigation": "Aucune enquête",
        "All investigations": "Toutes les enquêtes",
        "Unassigned searches": "Recherches non attribuées",
        "Active investigation": "Enquête active",
        "Open": "Ouvrir",
        "New": "Nouvelle",
        "Edit": "Modifier",
        "Archive": "Archiver",
        "Delete": "Supprimer",
        "New investigation": "Nouvelle enquête",
        "Edit investigation": "Modifier l'enquête",
        "Title": "Titre",
        "Reference": "Référence",
        "Description": "Description",
        "Tags": "Tags",
        "OSINT filters": "Filtres OSINT",
        "Search engines": "Moteurs de recherche",
        "Site": "Site",
        "Exclude": "Exclure",
        "Page text": "Texte de la page",
        "File": "Fichier",
        "Country": "Pays",
        "After": "Après",
        "Before": "Avant",
        "Clear filters": "Effacer les filtres",
        "Automatic dorks": "Dorks automatiques",
        "Results": "Résultats",
        "Query variants (optional)": "Variantes de requête (facultatif)",
        "Suggest variants": "Suggérer des variantes",
        "Manual variant": "Variante manuelle",
        "Add": "Ajouter",
        "Clear variants": "Effacer les variantes",
        "No additional variant selected.": "Aucune variante supplémentaire sélectionnée.",
        "The main query always runs. Suggested variants run only after you explicitly select them.": "La requête principale est toujours exécutée. Les variantes suggérées ne sont lancées qu'après votre sélection explicite.",
        "Search local archive": "Rechercher dans l'archive locale",
        "Local archive filters": "Filtres de l'archive locale",
        "Stored content": "Contenu enregistré",
        "Engine": "Moteur",
        "All engines": "Tous les moteurs",
        "Analyst status": "Statut analyste",
        "All statuses": "Tous les statuts",
        "To verify": "À vérifier",
        "Relevant": "Pertinent",
        "Confirmed": "Confirmé",
        "Discarded": "Écarté",
        "Domain": "Domaine",
        "Observed after": "Observé après",
        "Observed before": "Observé avant",
        "Search locally": "Rechercher localement",
        "Rebuild index": "Reconstruire l'index",
        "Data management": "Gestion des données",
        "Data": "Données",
        "Clear Synthesix history": "Effacer l'historique Synthesix",
        "Clear browser data": "Effacer les données du navigateur",
        "Closing all Synthesix tabs stops the program.": "La fermeture de tous les onglets Synthesix arrête le programme.",
        "Local archive search reads only the SQLite database and never launches an external search engine.": "La recherche locale consulte uniquement la base SQLite et ne lance jamais de moteur de recherche externe.",
        "This report uses only the local SQLite index. No external search engine was contacted.": "Ce rapport utilise uniquement l'index SQLite local. Aucun moteur de recherche externe n'a été contacté.",
        "Processing...": "Traitement en cours...",
        "Refresh": "Actualiser",
        "Overview": "Vue d'ensemble",
        "Saved pages": "Pages enregistrées",
        "Monitoring": "Surveillance",
        "Exports": "Exports",
        "Attach search": "Associer une recherche",
        "Search runs": "Recherches exécutées",
        "Provenance": "Provenance",
        "Interoperability": "Interopérabilité",
        "ZeroNeurone export": "Export ZeroNeurone",
        "Export GraphML and CSV": "Exporter GraphML et CSV",
        "Include evidence files as assets": "Inclure les fichiers de preuve comme assets",
        "Include proposed and rejected entity candidates": "Inclure les entités proposées et rejetées",
        "Delete export": "Supprimer l'export",
        "Extract entities": "Extraire les entités",
        "Proposed": "Proposée",
        "Validated": "Validée",
        "Rejected": "Rejetée",
        "Delete this extracted entity?": "Supprimer cette entité extraite ?",
        "Delete this ZeroNeurone export and its files?": "Supprimer cet export ZeroNeurone et ses fichiers ?",
        "No entity candidate extracted yet.": "Aucune entité candidate extraite.",
        "No ZeroNeurone export has been generated yet.": "Aucun export ZeroNeurone n'a encore été généré.",
        "Generating export...": "Génération de l'export...",
        "Attach": "Associer",
        "Date": "Date",
        "Query": "Requête",
        "Engines": "Moteurs",
        "Report": "Rapport",
        "Offline collection": "Collection hors ligne",
        "Local archive results": "Résultats de l'archive locale",
        "Already observed": "Déjà observé",
        "Context": "Contexte",
        "Status": "Statut",
        "First seen": "Première observation",
        "Last seen": "Dernière observation",
        "Notes": "Notes",
        "Unknown source": "Source inconnue",
        "Not reviewed": "Non examiné",
        "All local observations": "Toutes les observations locales",
        "No stored observation matches these filters.": "Aucune observation enregistrée ne correspond à ces filtres.",
        "Previous archive": "Archive précédente",
        "Current archive": "Archive actuelle",
        "Text similarity": "Similarité du texte",
        "Normalized text difference": "Différence du texte normalisé",
        "No textual difference available.": "Aucune différence textuelle disponible.",
        "No content change": "Aucun changement de contenu",
        "Minor change": "Changement mineur",
        "Significant content change": "Changement significatif du contenu",
        "Comparison inconclusive": "Comparaison non concluante",
        "Unavailable": "Indisponible",
        "What are you investigating?": "Sur quoi enquêtez-vous ?",
        "Exact alternative query": "Requête alternative exacte",
        "Title, description, URL, notes, tags...": "Titre, description, URL, notes, tags...",
        "priority, person, company": "priorité, personne, entreprise"
    };

    const multilingual = {
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
        "No results matched this search. Adjust the query, filters, or engines and try again.": ["Aucun résultat ne correspond à cette recherche. Ajustez la requête, les filtres ou les moteurs et réessayez.","Ningún resultado coincide con esta búsqueda. Ajusta la consulta, los filtros o los motores e inténtalo de nuevo.","没有结果匹配此次搜索。请调整查询、筛选条件或搜索引擎后重试。"],
        "Investigation search": ["Recherche d'enquête","Búsqueda de investigación","调查检索"],
        "Search and active investigation": ["Recherche et enquête active","Búsqueda e investigación activa","搜索与当前调查"],
        "Advanced tools": ["Outils avancés","Herramientas avanzadas","高级工具"],
        "Query preview": ["Aperçu de la requête","Vista previa de la consulta","查询预览"],
        "Personne, Suspect, custom tag...": ["Personne, Suspect, tag personnalisé...","Personne, Suspect, etiqueta personalizada...","Personne、Suspect、自定义标签……"],
        "Choose a suggested tag or enter custom comma-separated tags.": ["Choisissez un tag suggéré ou saisissez des tags personnalisés séparés par des virgules.","Elige una etiqueta sugerida o introduce etiquetas personalizadas separadas por comas.","选择建议的标签，或输入以逗号分隔的自定义标签。"],
        "Add suggested tag...": ["Ajouter un tag suggéré...","Añadir etiqueta sugerida...","添加建议的标签……"],
        "Add tag": ["Ajouter le tag","Añadir etiqueta","添加标签"],
        "Multi-engine search": ["Recherche multi-moteurs","Búsqueda multimotor","多引擎搜索"],
        "Investigation workspace": ["Espace d'enquête","Espacio de investigación","调查工作区"],
        "Search history": ["Historique des recherches","Historial de búsquedas","搜索历史"],
        "Search results": ["Résultats de recherche","Resultados de búsqueda","搜索结果"],
        "Local archive search": ["Recherche dans l'archive locale","Búsqueda en el archivo local","本地档案搜索"],
        "Search, compare, synthesize.": ["Rechercher, comparer, synthétiser.","Buscar, comparar, sintetizar.","搜索、比较、综合。"],
        "Search workspace": ["Espace de recherche","Espacio de búsqueda","搜索工作区"],
        "Search": ["Rechercher","Buscar","搜索"],
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
        "Refresh": ["Actualiser","Actualizar","刷新"],
        "Click to refresh.": ["Cliquez pour actualiser.","Haz clic para actualizar.","点击刷新。"],
        "Processing...": ["Traitement en cours...","Procesando...","处理中..."],
        "Checking VPN": ["Vérification du VPN","Comprobando VPN","正在检查 VPN"],
        "Checking VPN status": ["Vérification du statut VPN","Comprobando el estado de la VPN","正在检查 VPN 状态"],
        "Checking the public IP used by Chrome.": ["Vérification de l'adresse IP publique utilisée par Chrome.","Comprobando la IP pública utilizada por Chrome.","正在检查 Chrome 使用的公网 IP。"],
        "Checking the public IP used by Chrome. Click to refresh.": ["Vérification de l'adresse IP publique utilisée par Chrome. Cliquez pour actualiser.","Comprobando la IP pública utilizada por Chrome. Haz clic para actualizar.","正在检查 Chrome 使用的公网 IP。点击刷新。"],
        "VPN likely": ["VPN probable","VPN probable","可能使用 VPN"],
        "VPN not detected": ["VPN non détecté","VPN no detectada","未检测到 VPN"],
        "VPN unknown": ["VPN inconnu","Estado VPN desconocido","VPN 状态未知"],
        "Investigation": ["Enquête","Investigación","调查"],
        "Investigations": ["Enquêtes","Investigaciones","调查"],
        "No investigation": ["Aucune enquête","Sin investigación","无调查"],
        "All investigations": ["Toutes les enquêtes","Todas las investigaciones","所有调查"],
        "Unassigned searches": ["Recherches non attribuées","Búsquedas sin asignar","未分配的搜索"],
        "Active investigation": ["Enquête active","Investigación activa","当前调查"],
        "Open": ["Ouvrir","Abrir","打开"],
        "New": ["Nouvelle","Nueva","新建"],
        "Edit": ["Modifier","Editar","编辑"],
        "Archive": ["Archiver","Archivar","归档"],
        "Delete": ["Supprimer","Eliminar","删除"],
        "New investigation": ["Nouvelle enquête","Nueva investigación","新建调查"],
        "Edit investigation": ["Modifier l'enquête","Editar investigación","编辑调查"],
        "Title": ["Titre","Título","标题"],
        "Reference": ["Référence","Referencia","参考"],
        "Description": ["Description","Descripción","描述"],
        "Tags": ["Tags","Etiquetas","标签"],
        "OSINT filters": ["Filtres OSINT","Filtros OSINT","OSINT 筛选器"],
        "OSINT search filters": ["Filtres de recherche OSINT","Filtros de búsqueda OSINT","OSINT 搜索筛选器"],
        "Search engines": ["Moteurs de recherche","Motores de búsqueda","搜索引擎"],
        "Site": ["Site","Sitio","站点"],
        "Exclude": ["Exclure","Excluir","排除"],
        "Page text": ["Texte de la page","Texto de la página","页面文本"],
        "File": ["Fichier","Archivo","文件"],
        "Country": ["Pays","País","国家/地区"],
        "After": ["Après","Después","之后"],
        "Before": ["Avant","Antes","之前"],
        "Clear filters": ["Effacer les filtres","Borrar filtros","清除筛选器"],
        "Automatic dorks": ["Dorks automatiques","Dorks automáticos","自动高级查询"],
        "Quote simple searches automatically for exact matching": ["Mettre automatiquement les recherches simples entre guillemets pour une correspondance exacte","Entrecomillar automáticamente las búsquedas simples para coincidencias exactas","自动为简单搜索添加引号以进行精确匹配"],
        "Results": ["Résultats","Resultados","结果"],
        "Query variants (optional)": ["Variantes de requête (facultatif)","Variantes de consulta (opcional)","查询变体（可选）"],
        "Suggest variants": ["Suggérer des variantes","Sugerir variantes","建议变体"],
        "Manual variant": ["Variante manuelle","Variante manual","手动变体"],
        "Manual variant.": ["Variante manuelle.","Variante manual.","手动变体。"],
        "Add": ["Ajouter","Añadir","添加"],
        "Clear variants": ["Effacer les variantes","Borrar variantes","清除变体"],
        "No additional variant selected.": ["Aucune variante supplémentaire sélectionnée.","No se ha seleccionado ninguna variante adicional.","未选择其他变体。"],
        "The main query always runs. Suggested variants run only after you explicitly select them.": ["La requête principale est toujours exécutée. Les variantes suggérées ne sont lancées qu'après votre sélection explicite.","La consulta principal siempre se ejecuta. Las variantes sugeridas solo se ejecutan tras seleccionarlas explícitamente.","主查询始终运行。建议的变体仅在您明确选择后运行。"],
        "Search local archive": ["Rechercher dans l'archive locale","Buscar en el archivo local","搜索本地档案"],
        "Local archive filters": ["Filtres de l'archive locale","Filtros del archivo local","本地档案筛选器"],
        "Stored content": ["Contenu enregistré","Contenido almacenado","已存内容"],
        "Engine": ["Moteur","Motor","引擎"],
        "All engines": ["Tous les moteurs","Todos los motores","所有引擎"],
        "Analyst status": ["Statut analyste","Estado del analista","分析员状态"],
        "All statuses": ["Tous les statuts","Todos los estados","所有状态"],
        "To verify": ["À vérifier","Por verificar","待验证"],
        "Relevant": ["Pertinent","Relevante","相关"],
        "Confirmed": ["Confirmé","Confirmado","已确认"],
        "Discarded": ["Écarté","Descartado","已排除"],
        "Domain": ["Domaine","Dominio","域名"],
        "Observed after": ["Observé après","Observado después de","观察时间晚于"],
        "Observed before": ["Observé avant","Observado antes de","观察时间早于"],
        "Search locally": ["Rechercher localement","Buscar localmente","本地搜索"],
        "Rebuild index": ["Reconstruire l'index","Reconstruir índice","重建索引"],
        "Data management": ["Gestion des données","Gestión de datos","数据管理"],
        "Data": ["Données","Datos","数据"],
        "Clear Synthesix history": ["Effacer l'historique Synthesix","Borrar historial de Synthesix","清除 Synthesix 历史"],
        "Clear browser data": ["Effacer les données du navigateur","Borrar datos del navegador","清除浏览器数据"],
        "Closing all Synthesix tabs stops the program.": ["La fermeture de tous les onglets Synthesix arrête le programme.","Cerrar todas las pestañas de Synthesix detiene el programa.","关闭所有 Synthesix 标签页将停止程序。"],
        "Local archive search reads only the SQLite database and never launches an external search engine.": ["La recherche locale consulte uniquement la base SQLite et ne lance jamais de moteur de recherche externe.","La búsqueda local solo consulta la base SQLite y nunca inicia un motor de búsqueda externo.","本地档案搜索仅读取 SQLite 数据库，不会启动外部搜索引擎。"],
        "This report uses only the local SQLite index. No external search engine was contacted.": ["Ce rapport utilise uniquement l'index SQLite local. Aucun moteur de recherche externe n'a été contacté.","Este informe usa únicamente el índice SQLite local. No se contactó ningún motor externo.","此报告仅使用本地 SQLite 索引，未联系任何外部搜索引擎。"],
        "Overview": ["Vue d'ensemble","Resumen","概览"],
        "Saved pages": ["Pages enregistrées","Páginas guardadas","已保存页面"],
        "Monitoring": ["Surveillance","Monitorización","监控"],
        "Exports": ["Exports","Exportaciones","导出"],
        "Attach search": ["Associer une recherche","Vincular búsqueda","关联搜索"],
        "Search runs": ["Recherches exécutées","Ejecuciones de búsqueda","搜索运行"],
        "Investigation sections": ["Sections de l'enquête","Secciones de la investigación","调查章节"],
        "Investigation metrics": ["Mesures de l'enquête","Métricas de la investigación","调查指标"],
        "Saved investigation pages": ["Pages enregistrées dans l'enquête","Páginas guardadas de la investigación","调查中保存的页面"],
        "Page monitoring": ["Surveillance de page","Monitorización de página","页面监控"],
        "ZeroNeurone exports": ["Exports ZeroNeurone","Exportaciones ZeroNeurone","ZeroNeurone 导出"],
        "Attach existing search": ["Associer une recherche existante","Vincular búsqueda existente","关联现有搜索"],
        "Investigation searches": ["Recherches de l'enquête","Búsquedas de la investigación","调查搜索"],
        "Provenance": ["Provenance","Procedencia","来源"],
        "Interoperability": ["Interopérabilité","Interoperabilidad","互操作性"],
        "ZeroNeurone export": ["Export ZeroNeurone","Exportación ZeroNeurone","ZeroNeurone 导出"],
        "Export GraphML and CSV": ["Exporter GraphML et CSV","Exportar GraphML y CSV","导出 GraphML 和 CSV"],
        "Include evidence files as assets": ["Inclure les fichiers de preuve comme assets","Incluir archivos de evidencia como recursos","将证据文件作为资源包含"],
        "Include proposed and rejected entity candidates": ["Inclure les entités proposées et rejetées","Incluir entidades propuestas y rechazadas","包含建议和已拒绝的实体候选项"],
        "Delete export": ["Supprimer l'export","Eliminar exportación","删除导出"],
        "Extract entities": ["Extraire les entités","Extraer entidades","提取实体"],
        "Proposed": ["Proposée","Propuesta","已建议"],
        "Validated": ["Validée","Validada","已验证"],
        "Rejected": ["Rejetée","Rechazada","已拒绝"],
        "No entity candidate extracted yet.": ["Aucune entité candidate extraite.","Aún no se ha extraído ninguna entidad candidata.","尚未提取实体候选项。"],
        "No ZeroNeurone export has been generated yet.": ["Aucun export ZeroNeurone n'a encore été généré.","Aún no se ha generado ninguna exportación ZeroNeurone.","尚未生成 ZeroNeurone 导出。"],
        "Generating export...": ["Génération de l'export...","Generando exportación...","正在生成导出..."],
        "Attach": ["Associer","Vincular","关联"],
        "Date": ["Date","Fecha","日期"],
        "Query": ["Requête","Consulta","查询"],
        "Engines": ["Moteurs","Motores","引擎"],
        "Report": ["Rapport","Informe","报告"],
        "Offline collection": ["Collection hors ligne","Colección sin conexión","离线集合"],
        "Local archive results": ["Résultats de l'archive locale","Resultados del archivo local","本地档案结果"],
        "Already observed": ["Déjà observé","Ya observado","已观察"],
        "Context": ["Contexte","Contexto","上下文"],
        "Status": ["Statut","Estado","状态"],
        "First seen": ["Première observation","Primera observación","首次发现"],
        "Last seen": ["Dernière observation","Última observación","最后发现"],
        "Notes": ["Notes","Notas","备注"],
        "Unknown": ["Inconnu","Desconocido","未知"],
        "Unknown source": ["Source inconnue","Fuente desconocida","未知来源"],
        "Not reviewed": ["Non examiné","Sin revisar","未审核"],
        "All local observations": ["Toutes les observations locales","Todas las observaciones locales","所有本地观察"],
        "No stored observation matches these filters.": ["Aucune observation enregistrée ne correspond à ces filtres.","Ninguna observación almacenada coincide con estos filtros.","没有已存观察符合这些筛选条件。"],
        "Previous archive": ["Archive précédente","Archivo anterior","上一个归档"],
        "Current archive": ["Archive actuelle","Archivo actual","当前归档"],
        "Previous SHA-256": ["SHA-256 précédent","SHA-256 anterior","上一个 SHA-256"],
        "Current SHA-256": ["SHA-256 actuel","SHA-256 actual","当前 SHA-256"],
        "Text similarity": ["Similarité du texte","Similitud del texto","文本相似度"],
        "Minor changes above the configured similarity threshold are separated from significant changes to reduce alerts caused by dynamic page details.": ["Les changements mineurs au-dessus du seuil de similarité configuré sont séparés des changements significatifs afin de réduire les alertes causées par les détails dynamiques de la page.","Los cambios menores por encima del umbral de similitud configurado se separan de los cambios significativos para reducir las alertas causadas por detalles dinámicos de la página.","超过配置相似度阈值的轻微变化会与显著变化分开，以减少页面动态细节造成的警报。"],
        "Normalized text difference": ["Différence du texte normalisé","Diferencia de texto normalizado","规范化文本差异"],
        "No textual difference available.": ["Aucune différence textuelle disponible.","No hay diferencias textuales disponibles.","没有可用的文本差异。"],
        "No content change": ["Aucun changement de contenu","Sin cambios de contenido","内容无变化"],
        "Minor change": ["Changement mineur","Cambio menor","轻微变化"],
        "Significant change": ["Changement significatif","Cambio significativo","显著变化"],
        "Significant content change": ["Changement significatif du contenu","Cambio significativo de contenido","内容发生显著变化"],
        "Inconclusive": ["Non concluant","No concluyente","无法确定"],
        "Comparison inconclusive": ["Comparaison non concluante","Comparación no concluyente","比较结果不确定"],
        "Unavailable": ["Indisponible","No disponible","不可用"],
        "What are you investigating?": ["Sur quoi enquêtez-vous ?","¿Qué estás investigando?","您正在调查什么？"],
        "Exact alternative query": ["Requête alternative exacte","Consulta alternativa exacta","精确替代查询"],
        "Title, description, URL, notes, tags...": ["Titre, description, URL, notes, tags...","Título, descripción, URL, notas, etiquetas...","标题、描述、URL、备注、标签..."],
        "Title, URL, notes, tags...": ["Titre, URL, notes, tags...","Título, URL, notas, etiquetas...","标题、URL、备注、标签..."],
        "Add verification notes, context, or caveats.": ["Ajouter des notes de vérification, du contexte ou des réserves.","Añadir notas de verificación, contexto o advertencias.","添加验证备注、上下文或注意事项。"],
        "Sweden or SE": ["Suède ou SE","Suecia o SE","瑞典或 SE"],
        "Previous searches": ["Recherches précédentes","Búsquedas anteriores","历史搜索"],
        "Search query": ["Requête de recherche","Consulta de búsqueda","搜索查询"],
        "URL": ["URL","URL","URL"],
        "Phone": ["Téléphone","Teléfono","电话"],
        "Handle": ["Identifiant de compte","Usuario","账号"],
        "Identifier": ["Identifiant","Identificador","标识符"],
        "Coordinates": ["Coordonnées","Coordenadas","坐标"],
        "Text": ["Texte","Texto","文本"],
        "Page archive": ["Archive de page","Archivo de página","页面归档"],
        "Selected area": ["Zone sélectionnée","Área seleccionada","选定区域"],
        "Visible area": ["Zone visible","Área visible","可见区域"],
        "Untitled result": ["Résultat sans titre","Resultado sin título","无标题结果"],
        "Favorite": ["Favori","Favorito","收藏"],
        "Score component": ["Composante du score","Componente de puntuación","评分组成"],
        "Waiting for baseline": ["En attente d'une référence","Esperando línea base","等待基线"],
        "No report": ["Aucun rapport","Sin informe","无报告"],
        "Filter-only search": ["Recherche avec filtres uniquement","Búsqueda solo con filtros","仅筛选搜索"],
        "Legacy": ["Hérité","Heredado","旧版"],
        "Nodes CSV": ["CSV des nœuds","CSV de nodos","节点 CSV"],
        "Edges CSV": ["CSV des liens","CSV de enlaces","边 CSV"],
        "Manifest": ["Manifeste","Manifiesto","清单"],
        "Dossier JSON": ["Dossier JSON","Dossier JSON","Dossier JSON"],
        "Search Results for": ["Résultats de recherche pour","Resultados de búsqueda para","搜索结果"],
        "Total time": ["Temps total","Tiempo total","总用时"],
        "Created": ["Créé","Creado","创建时间"],
        "All": ["Tous","Todos","全部"],
        "Archived": ["Archivée","Archivada","已归档"],
        "Previous search": ["Recherche précédente","Búsqueda anterior","上一次搜索"],
        "Synthesix History": ["Historique Synthesix","Historial de Synthesix","Synthesix 历史"],
        "Page comparison - Synthesix": ["Comparaison de page - Synthesix","Comparación de páginas - Synthesix","页面比较 - Synthesix"],
        "Synthesix page monitoring": ["Surveillance de page Synthesix","Monitorización de páginas de Synthesix","Synthesix 页面监控"],
        "Original Query": ["Requête d'origine","Consulta original","原始查询"],
        "Smart Query": ["Requête optimisée","Consulta optimizada","优化查询"],
        "Number of results": ["Nombre de résultats","Número de resultados","结果数量"],
        "Link to results": ["Lien vers les résultats","Enlace a los resultados","结果链接"],
        "View results": ["Voir les résultats","Ver resultados","查看结果"],
        "Retry": ["Réessayer","Reintentar","重试"],
        "Exact query": ["Requête exacte","Consulta exacta","精确查询"],
        "Counts distinguish successful zero-result searches from timeouts, challenges, and other errors.": ["Les nombres distinguent les recherches réussies sans résultat des expirations, blocages et autres erreurs.","Los recuentos distinguen las búsquedas correctas sin resultados de los tiempos de espera, bloqueos y otros errores.","计数可区分成功但无结果的搜索、超时、验证拦截和其他错误。"],
        "No relevant results found": ["Aucun résultat pertinent trouvé","No se encontraron resultados relevantes","未找到相关结果"],
        "Link": ["Lien","Enlace","链接"],
        "Source": ["Source","Fuente","来源"],
        "Score": ["Score","Puntuación","评分"],
        "Searches": ["Recherches","Búsquedas","搜索"],
        "Favorites": ["Favoris","Favoritos","收藏"],
        "Analyst selection": ["Sélection de l'analyste","Selección del analista","分析员选择"],
        "All sources": ["Toutes les sources","Todas las fuentes","所有来源"],
        "All tags": ["Tous les tags","Todas las etiquetas","所有标签"],
        "Temporal comparison": ["Comparaison temporelle","Comparación temporal","时间比较"],
        "Existing collection": ["Collection existante","Colección existente","现有集合"],
        "Attach a previous search": ["Associer une recherche précédente","Adjuntar una búsqueda anterior","关联历史搜索"],
        "Select a search": ["Sélectionner une recherche","Seleccionar una búsqueda","选择搜索"],
        "Entity review status": ["Statut de validation de l'entité","Estado de revisión de la entidad","实体审核状态"],
        "Partial capture": ["Capture partielle","Captura parcial","部分捕获"],
        "Verify": ["Vérifier","Verificar","验证"],
        "Stop": ["Arrêter","Detener","停止"],
        "Monitor changes": ["Surveiller les changements","Monitorizar cambios","监控更改"],
        "Found through search": ["Trouvé par la recherche","Encontrado mediante búsqueda","通过搜索找到"],
        "Open referring page": ["Ouvrir la page référente","Abrir página de referencia","打开引用页面"],
        "Saved while browsing": ["Enregistré pendant la navigation","Guardado durante la navegación","浏览时保存"],
        "Analyst notes and tags": ["Notes et tags de l'analyste","Notas y etiquetas del analista","分析员备注和标签"],
        "Save notes": ["Enregistrer les notes","Guardar notas","保存备注"],
        "Open comparison": ["Ouvrir la comparaison","Abrir comparación","打开比较"],
        "Archive the page twice to generate a comparison.": ["Archivez la page deux fois pour générer une comparaison.","Archiva la página dos veces para generar una comparación.","将页面归档两次以生成比较。"],
        "Stop monitoring": ["Arrêter la surveillance","Detener monitorización","停止监控"],
        "No search attached.": ["Aucune recherche associée.","No hay ninguna búsqueda adjunta.","未关联搜索。"],
        "This investigation is archived and read-only.": ["Cette enquête est archivée et en lecture seule.","Esta investigación está archivada y es de solo lectura.","此调查已归档且为只读。"],
        "not run": ["non exécuté","no ejecutado","未运行"],
        "timeout": ["expiration","tiempo de espera agotado","超时"],
        "challenge": ["blocage anti-robot","bloqueo antirrobot","反机器人验证"],
        "error": ["erreur","error","错误"],
        "No previous searches yet.": ["Aucune recherche précédente.","Todavía no hay búsquedas anteriores.","暂无历史搜索。"],
        "No matching searches.": ["Aucune recherche correspondante.","No hay búsquedas coincidentes.","没有匹配的搜索。"],
        "Please enter a search term or filter.": ["Saisissez un terme de recherche ou un filtre.","Introduce un término de búsqueda o un filtro.","请输入搜索词或筛选条件。"],
        "The After date must be earlier than or equal to the Before date.": ["La date Après doit être antérieure ou égale à la date Avant.","La fecha Después debe ser anterior o igual a la fecha Antes.","“之后”日期必须早于或等于“之前”日期。"],
        "Archived investigations are read-only. Select an active investigation.": ["Les enquêtes archivées sont en lecture seule. Sélectionnez une enquête active.","Las investigaciones archivadas son de solo lectura. Selecciona una investigación activa.","已归档调查为只读。请选择当前调查。"],
        "Observed after must be earlier than or equal to observed before.": ["La date « observé après » doit être antérieure ou égale à « observé avant ».","La fecha «observado después» debe ser anterior o igual a «observado antes».","“观察时间晚于”必须早于或等于“观察时间早于”。"],
        "Select the query variants to execute.": ["Sélectionnez les variantes de requête à exécuter.","Selecciona las variantes de consulta que se ejecutarán.","请选择要运行的查询变体。"],
        "No safe automatic variant was suggested.": ["Aucune variante automatique sûre n'a été suggérée.","No se sugirió ninguna variante automática segura.","未建议任何安全的自动变体。"],
        "Enter a main query before requesting variants.": ["Saisissez une requête principale avant de demander des variantes.","Introduce una consulta principal antes de solicitar variantes.","请先输入主查询，再请求变体。"],
        "Delete all Synthesix search history and generated result reports? Investigation folders and explicitly saved pages are preserved.": ["Supprimer tout l'historique de recherche Synthesix et les rapports générés ? Les dossiers d'enquête et les pages explicitement enregistrées sont conservés.","¿Eliminar todo el historial de búsqueda de Synthesix y los informes generados? Se conservarán las carpetas de investigación y las páginas guardadas explícitamente.","是否删除所有 Synthesix 搜索历史和生成的结果报告？调查文件夹和明确保存的页面将保留。"],
        "Clear history, cookies, cache, and site data from the Synthesix browser profile? Saved sessions will be signed out.": ["Effacer l'historique, les cookies, le cache et les données de sites du profil navigateur Synthesix ? Les sessions enregistrées seront déconnectées.","¿Borrar historial, cookies, caché y datos de sitios del perfil de navegador de Synthesix? Se cerrarán las sesiones guardadas.","是否清除 Synthesix 浏览器配置中的历史、Cookie、缓存和网站数据？已保存的会话将退出登录。"],
        "Remove this page from the investigation? The underlying search observation is preserved.": ["Retirer cette page de l'enquête ? L'observation de recherche sous-jacente est conservée.","¿Quitar esta página de la investigación? Se conservará la observación de búsqueda subyacente.","是否从调查中移除此页面？底层搜索观察将保留。"],
        "Delete this evidence capture and its files?": ["Supprimer cette capture de preuve et ses fichiers ?","¿Eliminar esta captura de evidencia y sus archivos?","是否删除此证据捕获及其文件？"],
        "Stop monitoring this page?": ["Arrêter la surveillance de cette page ?","¿Dejar de monitorizar esta página?","是否停止监控此页面？"],
        "Delete this extracted entity?": ["Supprimer cette entité extraite ?","¿Eliminar esta entidad extraída?","是否删除此提取实体？"],
        "Delete this ZeroNeurone export and its files?": ["Supprimer cet export ZeroNeurone et ses fichiers ?","¿Eliminar esta exportación ZeroNeurone y sus archivos?","是否删除此 ZeroNeurone 导出及其文件？"],
        "Checking...": ["Vérification...","Comprobando...","检查中..."],
        "The public IP is listed as a known VPN exit node. Detection can be wrong.": ["L'adresse IP publique est répertoriée comme nœud de sortie VPN connu. La détection peut être erronée.","La IP pública figura como un nodo de salida VPN conocido. La detección puede ser incorrecta.","该公网 IP 被列为已知 VPN 出口节点，检测结果可能有误。"],
        "The public IP is not listed as a known VPN exit node. This does not prove that a VPN is off.": ["L'adresse IP publique n'est pas répertoriée comme nœud de sortie VPN connu. Cela ne prouve pas qu'aucun VPN n'est actif.","La IP pública no figura como un nodo de salida VPN conocido. Esto no demuestra que la VPN esté desactivada.","该公网 IP 未被列为已知 VPN 出口节点，但这不能证明 VPN 已关闭。"],
        "The external VPN check is unavailable or timed out.": ["La vérification VPN externe est indisponible ou a expiré.","La comprobación VPN externa no está disponible o agotó el tiempo.","外部 VPN 检查不可用或已超时。"],
        "VPN status is missing": ["Le statut VPN est absent","Falta el estado de la VPN","缺少 VPN 状态"],
        "This report action is invalid.": ["Cette action de rapport est invalide.","Esta acción del informe no es válida.","此报告操作无效。"],
        "Open report": ["Ouvrir le rapport","Abrir informe","打开报告"],
        "Delete this capture and its local evidence files": ["Supprimer cette capture et ses fichiers de preuve locaux","Eliminar esta captura y sus archivos de evidencia locales","删除此捕获及其本地证据文件"],
        "Add or remove this page from favorites": ["Ajouter ou retirer cette page des favoris","Añadir o quitar esta página de favoritos","添加或移除此页面的收藏状态"],
        "Remove this saved page from the investigation": ["Retirer cette page enregistrée de l'enquête","Quitar esta página guardada de la investigación","从调查中移除此已保存页面"]
    };

    const languageIndexes = {fr: 0, es: 1, zh: 2};

    const additionalTranslations = {
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
        "No results matched this search. Adjust the query, filters, or engines and try again.": ["Nenhum resultado corresponde a esta pesquisa. Ajuste a consulta, os filtros ou os motores e tente novamente.", "Keine Ergebnisse für diese Suche. Passen Sie Abfrage, Filter oder Suchmaschinen an und versuchen Sie es erneut."],
        "Investigation search": ["Pesquisa de investigação", "Ermittlungssuche"],
        "Search and active investigation": ["Pesquisa e investigação ativa", "Suche und aktive Ermittlung"],
        "Advanced tools": ["Ferramentas avançadas", "Erweiterte Werkzeuge"],
        "Query preview": ["Pré-visualização da consulta", "Abfragevorschau"],
        "Personne, Suspect, custom tag...": ["Personne, Suspect, etiqueta personalizada...", "Personne, Suspect, eigenes Tag..."],
        "Choose a suggested tag or enter custom comma-separated tags.": ["Escolha uma etiqueta sugerida ou introduza etiquetas personalizadas separadas por vírgulas.", "Wählen Sie ein vorgeschlagenes Tag oder geben Sie eigene, durch Kommas getrennte Tags ein."],
        "Add suggested tag...": ["Adicionar etiqueta sugerida...", "Vorgeschlagenes Tag hinzufügen..."],
        "Add tag": ["Adicionar etiqueta", "Tag hinzufügen"],
        "Multi-engine search": ["Pesquisa multimotor", "Multi-Suchmaschine"],
        "Investigation workspace": ["Espaço de investigação", "Ermittlungsbereich"],
        "Search history": ["Histórico de pesquisas", "Suchverlauf"],
        "Search results": ["Resultados da pesquisa", "Suchergebnisse"],
        "Local archive search": ["Pesquisa no arquivo local", "Lokale Archivsuche"],
        "Search, compare, synthesize.": ["Pesquise, compare, sintetize.", "Suchen, vergleichen, zusammenführen."],
        "Search workspace": ["Espaço de pesquisa", "Suchbereich"],
        "Search": ["Pesquisar", "Suchen"],
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
        "Refresh": ["Atualizar", "Aktualisieren"],
        "Click to refresh.": ["Clique para atualizar.", "Zum Aktualisieren klicken."],
        "Processing...": ["A processar...", "Verarbeitung..."],
        "Checking VPN": ["A verificar a VPN", "VPN wird geprüft"],
        "Checking VPN status": ["A verificar o estado da VPN", "VPN-Status wird geprüft"],
        "Checking the public IP used by Chrome.": ["A verificar o IP público utilizado pelo Chrome.", "Die von Chrome verwendete öffentliche IP wird geprüft."],
        "Checking the public IP used by Chrome. Click to refresh.": ["A verificar o IP público utilizado pelo Chrome. Clique para atualizar.", "Die von Chrome verwendete öffentliche IP wird geprüft. Zum Aktualisieren klicken."],
        "VPN likely": ["VPN provável", "VPN wahrscheinlich"],
        "VPN not detected": ["VPN não detetada", "Kein VPN erkannt"],
        "VPN unknown": ["VPN desconhecida", "VPN-Status unbekannt"],
        "Investigation": ["Investigação", "Ermittlung"],
        "Investigations": ["Investigações", "Ermittlungen"],
        "No investigation": ["Sem investigação", "Keine Ermittlung"],
        "All investigations": ["Todas as investigações", "Alle Ermittlungen"],
        "Unassigned searches": ["Pesquisas não atribuídas", "Nicht zugeordnete Suchen"],
        "Active investigation": ["Investigação ativa", "Aktive Ermittlung"],
        "Open": ["Abrir", "Öffnen"],
        "New": ["Nova", "Neu"],
        "Edit": ["Editar", "Bearbeiten"],
        "Archive": ["Arquivar", "Archivieren"],
        "Delete": ["Eliminar", "Löschen"],
        "New investigation": ["Nova investigação", "Neue Ermittlung"],
        "Edit investigation": ["Editar investigação", "Ermittlung bearbeiten"],
        "Title": ["Título", "Titel"],
        "Reference": ["Referência", "Referenz"],
        "Description": ["Descrição", "Beschreibung"],
        "Tags": ["Etiquetas", "Tags"],
        "OSINT filters": ["Filtros OSINT", "OSINT-Filter"],
        "OSINT search filters": ["Filtros de pesquisa OSINT", "OSINT-Suchfilter"],
        "Search engines": ["Motores de pesquisa", "Suchmaschinen"],
        "Site": ["Site", "Website"],
        "Exclude": ["Excluir", "Ausschließen"],
        "Page text": ["Texto da página", "Seitentext"],
        "File": ["Ficheiro", "Datei"],
        "Country": ["País", "Land"],
        "After": ["Depois", "Nach"],
        "Before": ["Antes", "Vor"],
        "Clear filters": ["Limpar filtros", "Filter löschen"],
        "Automatic dorks": ["Dorks automáticos", "Automatische Dorks"],
        "Quote simple searches automatically for exact matching": ["Colocar automaticamente pesquisas simples entre aspas para correspondência exata", "Einfache Suchen für genaue Treffer automatisch in Anführungszeichen setzen"],
        "Results": ["Resultados", "Ergebnisse"],
        "Query variants (optional)": ["Variantes da consulta (opcional)", "Abfragevarianten (optional)"],
        "Suggest variants": ["Sugerir variantes", "Varianten vorschlagen"],
        "Manual variant": ["Variante manual", "Manuelle Variante"],
        "Manual variant.": ["Variante manual.", "Manuelle Variante."],
        "Add": ["Adicionar", "Hinzufügen"],
        "Clear variants": ["Limpar variantes", "Varianten löschen"],
        "No additional variant selected.": ["Nenhuma variante adicional selecionada.", "Keine zusätzliche Variante ausgewählt."],
        "The main query always runs. Suggested variants run only after you explicitly select them.": ["A consulta principal é sempre executada. As variantes sugeridas só são executadas depois de as selecionar explicitamente.", "Die Hauptabfrage wird immer ausgeführt. Vorgeschlagene Varianten werden nur nach ausdrücklicher Auswahl ausgeführt."],
        "Search local archive": ["Pesquisar no arquivo local", "Lokales Archiv durchsuchen"],
        "Local archive filters": ["Filtros do arquivo local", "Filter des lokalen Archivs"],
        "Stored content": ["Conteúdo armazenado", "Gespeicherter Inhalt"],
        "Engine": ["Motor", "Suchmaschine"],
        "All engines": ["Todos os motores", "Alle Suchmaschinen"],
        "Analyst status": ["Estado do analista", "Analystenstatus"],
        "All statuses": ["Todos os estados", "Alle Status"],
        "To verify": ["A verificar", "Zu prüfen"],
        "Relevant": ["Relevante", "Relevant"],
        "Confirmed": ["Confirmado", "Bestätigt"],
        "Discarded": ["Descartado", "Verworfen"],
        "Domain": ["Domínio", "Domain"],
        "Observed after": ["Observado depois de", "Beobachtet nach"],
        "Observed before": ["Observado antes de", "Beobachtet vor"],
        "Search locally": ["Pesquisar localmente", "Lokal suchen"],
        "Rebuild index": ["Reconstruir índice", "Index neu erstellen"],
        "Data management": ["Gestão de dados", "Datenverwaltung"],
        "Data": ["Dados", "Daten"],
        "Clear Synthesix history": ["Limpar histórico do Synthesix", "Synthesix-Verlauf löschen"],
        "Clear browser data": ["Limpar dados do navegador", "Browserdaten löschen"],
        "Closing all Synthesix tabs stops the program.": ["Fechar todos os separadores do Synthesix para o programa.", "Das Schließen aller Synthesix-Tabs beendet das Programm."],
        "Local archive search reads only the SQLite database and never launches an external search engine.": ["A pesquisa no arquivo local lê apenas a base de dados SQLite e nunca inicia um motor de pesquisa externo.", "Die lokale Archivsuche liest nur die SQLite-Datenbank und startet keine externe Suchmaschine."],
        "This report uses only the local SQLite index. No external search engine was contacted.": ["Este relatório utiliza apenas o índice SQLite local. Nenhum motor de pesquisa externo foi contactado.", "Dieser Bericht verwendet nur den lokalen SQLite-Index. Es wurde keine externe Suchmaschine kontaktiert."],
        "Overview": ["Visão geral", "Übersicht"],
        "Saved pages": ["Páginas guardadas", "Gespeicherte Seiten"],
        "Monitoring": ["Monitorização", "Überwachung"],
        "Exports": ["Exportações", "Exporte"],
        "Attach search": ["Associar pesquisa", "Suche zuordnen"],
        "Search runs": ["Execuções de pesquisa", "Suchläufe"],
        "Investigation sections": ["Secções da investigação", "Ermittlungsbereiche"],
        "Investigation metrics": ["Métricas da investigação", "Ermittlungskennzahlen"],
        "Saved investigation pages": ["Páginas guardadas da investigação", "Gespeicherte Ermittlungsseiten"],
        "Page monitoring": ["Monitorização da página", "Seitenüberwachung"],
        "ZeroNeurone exports": ["Exportações ZeroNeurone", "ZeroNeurone-Exporte"],
        "Attach existing search": ["Associar pesquisa existente", "Vorhandene Suche zuordnen"],
        "Investigation searches": ["Pesquisas da investigação", "Ermittlungssuchen"],
        "Provenance": ["Proveniência", "Herkunft"],
        "Interoperability": ["Interoperabilidade", "Interoperabilität"],
        "ZeroNeurone export": ["Exportação ZeroNeurone", "ZeroNeurone-Export"],
        "Export GraphML and CSV": ["Exportar GraphML e CSV", "GraphML und CSV exportieren"],
        "Include evidence files as assets": ["Incluir ficheiros de prova como recursos", "Beweisdateien als Assets einschließen"],
        "Include proposed and rejected entity candidates": ["Incluir entidades candidatas propostas e rejeitadas", "Vorgeschlagene und abgelehnte Entitätskandidaten einschließen"],
        "Delete export": ["Eliminar exportação", "Export löschen"],
        "Extract entities": ["Extrair entidades", "Entitäten extrahieren"],
        "Proposed": ["Proposta", "Vorgeschlagen"],
        "Validated": ["Validada", "Validiert"],
        "Rejected": ["Rejeitada", "Abgelehnt"],
        "No entity candidate extracted yet.": ["Ainda não foi extraída nenhuma entidade candidata.", "Es wurde noch kein Entitätskandidat extrahiert."],
        "No ZeroNeurone export has been generated yet.": ["Ainda não foi gerada nenhuma exportação ZeroNeurone.", "Es wurde noch kein ZeroNeurone-Export erstellt."],
        "Generating export...": ["A gerar exportação...", "Export wird erstellt..."],
        "Attach": ["Associar", "Zuordnen"],
        "Date": ["Data", "Datum"],
        "Query": ["Consulta", "Abfrage"],
        "Engines": ["Motores", "Suchmaschinen"],
        "Report": ["Relatório", "Bericht"],
        "Offline collection": ["Coleção offline", "Offline-Sammlung"],
        "Local archive results": ["Resultados do arquivo local", "Ergebnisse des lokalen Archivs"],
        "Already observed": ["Já observado", "Bereits beobachtet"],
        "Context": ["Contexto", "Kontext"],
        "Status": ["Estado", "Status"],
        "First seen": ["Visto pela primeira vez", "Erstmals gesehen"],
        "Last seen": ["Visto pela última vez", "Zuletzt gesehen"],
        "Notes": ["Notas", "Notizen"],
        "Unknown": ["Desconhecido", "Unbekannt"],
        "Unknown source": ["Fonte desconhecida", "Unbekannte Quelle"],
        "Not reviewed": ["Não revisto", "Nicht geprüft"],
        "All local observations": ["Todas as observações locais", "Alle lokalen Beobachtungen"],
        "No stored observation matches these filters.": ["Nenhuma observação armazenada corresponde a estes filtros.", "Keine gespeicherte Beobachtung entspricht diesen Filtern."],
        "Previous archive": ["Arquivo anterior", "Vorheriges Archiv"],
        "Current archive": ["Arquivo atual", "Aktuelles Archiv"],
        "Previous SHA-256": ["SHA-256 anterior", "Vorheriger SHA-256"],
        "Current SHA-256": ["SHA-256 atual", "Aktueller SHA-256"],
        "Text similarity": ["Semelhança do texto", "Textähnlichkeit"],
        "Minor changes above the configured similarity threshold are separated from significant changes to reduce alerts caused by dynamic page details.": ["As alterações menores acima do limiar de semelhança configurado são separadas das alterações significativas para reduzir os alertas causados por detalhes dinâmicos da página.", "Kleinere Änderungen oberhalb des festgelegten Ähnlichkeitsschwellenwerts werden von wesentlichen Änderungen getrennt, um Warnungen durch dynamische Seitendetails zu reduzieren."],
        "Normalized text difference": ["Diferença do texto normalizado", "Normalisierter Textunterschied"],
        "No textual difference available.": ["Nenhuma diferença textual disponível.", "Kein Textunterschied verfügbar."],
        "No content change": ["Sem alteração do conteúdo", "Keine Inhaltsänderung"],
        "Minor change": ["Alteração menor", "Kleinere Änderung"],
        "Significant change": ["Alteração significativa", "Wesentliche Änderung"],
        "Significant content change": ["Alteração significativa do conteúdo", "Wesentliche Inhaltsänderung"],
        "Inconclusive": ["Inconclusivo", "Nicht eindeutig"],
        "Comparison inconclusive": ["Comparação inconclusiva", "Vergleich nicht eindeutig"],
        "Unavailable": ["Indisponível", "Nicht verfügbar"],
        "What are you investigating?": ["O que está a investigar?", "Was untersuchen Sie?"],
        "Exact alternative query": ["Consulta alternativa exata", "Exakte alternative Abfrage"],
        "Title, description, URL, notes, tags...": ["Título, descrição, URL, notas, etiquetas...", "Titel, Beschreibung, URL, Notizen, Tags..."],
        "Title, URL, notes, tags...": ["Título, URL, notas, etiquetas...", "Titel, URL, Notizen, Tags..."],
        "Add verification notes, context, or caveats.": ["Adicione notas de verificação, contexto ou ressalvas.", "Prüfnotizen, Kontext oder Vorbehalte hinzufügen."],
        "Sweden or SE": ["Suécia ou SE", "Schweden oder SE"],
        "Previous searches": ["Pesquisas anteriores", "Vorherige Suchen"],
        "Search query": ["Consulta de pesquisa", "Suchabfrage"],
        "URL": ["URL", "URL"],
        "Phone": ["Telefone", "Telefon"],
        "Handle": ["Nome de utilizador", "Benutzername"],
        "Identifier": ["Identificador", "Kennung"],
        "Coordinates": ["Coordenadas", "Koordinaten"],
        "Text": ["Texto", "Text"],
        "Page archive": ["Arquivo da página", "Seitenarchiv"],
        "Selected area": ["Área selecionada", "Ausgewählter Bereich"],
        "Visible area": ["Área visível", "Sichtbarer Bereich"],
        "Untitled result": ["Resultado sem título", "Ergebnis ohne Titel"],
        "Favorite": ["Favorito", "Favorit"],
        "Score component": ["Componente da pontuação", "Bewertungskomponente"],
        "Waiting for baseline": ["A aguardar referência", "Warten auf Ausgangswert"],
        "No report": ["Sem relatório", "Kein Bericht"],
        "Filter-only search": ["Pesquisa apenas com filtros", "Reine Filtersuche"],
        "Legacy": ["Legado", "Veraltet"],
        "Nodes CSV": ["CSV de nós", "Knoten-CSV"],
        "Edges CSV": ["CSV de ligações", "Kanten-CSV"],
        "Manifest": ["Manifesto", "Manifest"],
        "Dossier JSON": ["Dossier JSON", "Dossier JSON"],
        "Search Results for": ["Resultados da pesquisa para", "Suchergebnisse für"],
        "Total time": ["Tempo total", "Gesamtzeit"],
        "Created": ["Criado", "Erstellt"],
        "All": ["Todos", "Alle"],
        "Archived": ["Arquivada", "Archiviert"],
        "Previous search": ["Pesquisa anterior", "Vorherige Suche"],
        "Synthesix History": ["Histórico do Synthesix", "Synthesix-Verlauf"],
        "Page comparison - Synthesix": ["Comparação de páginas - Synthesix", "Seitenvergleich - Synthesix"],
        "Synthesix page monitoring": ["Monitorização de páginas do Synthesix", "Synthesix-Seitenüberwachung"],
        "Original Query": ["Consulta original", "Ursprüngliche Abfrage"],
        "Smart Query": ["Consulta otimizada", "Optimierte Abfrage"],
        "Number of results": ["Número de resultados", "Anzahl der Ergebnisse"],
        "Link to results": ["Ligação para os resultados", "Link zu den Ergebnissen"],
        "View results": ["Ver resultados", "Ergebnisse anzeigen"],
        "Retry": ["Tentar novamente", "Erneut versuchen"],
        "Exact query": ["Consulta exata", "Exakte Abfrage"],
        "Counts distinguish successful zero-result searches from timeouts, challenges, and other errors.": ["As contagens distinguem pesquisas bem-sucedidas sem resultados de tempos limite, bloqueios e outros erros.", "Die Zahlen unterscheiden erfolgreiche Suchen ohne Ergebnisse von Zeitüberschreitungen, Sperren und anderen Fehlern."],
        "No relevant results found": ["Nenhum resultado relevante encontrado", "Keine relevanten Ergebnisse gefunden"],
        "Link": ["Ligação", "Link"],
        "Source": ["Fonte", "Quelle"],
        "Score": ["Pontuação", "Bewertung"],
        "Searches": ["Pesquisas", "Suchen"],
        "Favorites": ["Favoritos", "Favoriten"],
        "Analyst selection": ["Seleção do analista", "Analystenauswahl"],
        "All sources": ["Todas as fontes", "Alle Quellen"],
        "All tags": ["Todas as etiquetas", "Alle Tags"],
        "Temporal comparison": ["Comparação temporal", "Zeitlicher Vergleich"],
        "Existing collection": ["Coleção existente", "Vorhandene Sammlung"],
        "Attach a previous search": ["Associar uma pesquisa anterior", "Vorherige Suche zuordnen"],
        "Select a search": ["Selecionar uma pesquisa", "Suche auswählen"],
        "Entity review status": ["Estado da revisão da entidade", "Prüfstatus der Entität"],
        "Partial capture": ["Captura parcial", "Teilaufnahme"],
        "Verify": ["Verificar", "Prüfen"],
        "Stop": ["Parar", "Beenden"],
        "Monitor changes": ["Monitorizar alterações", "Änderungen überwachen"],
        "Found through search": ["Encontrado através da pesquisa", "Über die Suche gefunden"],
        "Open referring page": ["Abrir página de referência", "Verweisende Seite öffnen"],
        "Saved while browsing": ["Guardado durante a navegação", "Beim Browsen gespeichert"],
        "Analyst notes and tags": ["Notas e etiquetas do analista", "Analystennotizen und Tags"],
        "Save notes": ["Guardar notas", "Notizen speichern"],
        "Open comparison": ["Abrir comparação", "Vergleich öffnen"],
        "Archive the page twice to generate a comparison.": ["Arquive a página duas vezes para gerar uma comparação.", "Archivieren Sie die Seite zweimal, um einen Vergleich zu erstellen."],
        "Stop monitoring": ["Parar monitorização", "Überwachung beenden"],
        "No search attached.": ["Nenhuma pesquisa associada.", "Keine Suche zugeordnet."],
        "This investigation is archived and read-only.": ["Esta investigação está arquivada e é só de leitura.", "Diese Ermittlung ist archiviert und schreibgeschützt."],
        "not run": ["não executado", "nicht ausgeführt"],
        "timeout": ["tempo limite", "Zeitüberschreitung"],
        "challenge": ["bloqueio antirrobô", "Anti-Bot-Prüfung"],
        "error": ["erro", "Fehler"],
        "No previous searches yet.": ["Ainda não existem pesquisas anteriores.", "Noch keine vorherigen Suchen."],
        "No matching searches.": ["Nenhuma pesquisa correspondente.", "Keine passenden Suchen."],
        "Please enter a search term or filter.": ["Introduza um termo de pesquisa ou filtro.", "Geben Sie einen Suchbegriff oder Filter ein."],
        "The After date must be earlier than or equal to the Before date.": ["A data Depois deve ser anterior ou igual à data Antes.", "Das Nach-Datum muss vor oder gleich dem Vor-Datum liegen."],
        "Archived investigations are read-only. Select an active investigation.": ["As investigações arquivadas são só de leitura. Selecione uma investigação ativa.", "Archivierte Ermittlungen sind schreibgeschützt. Wählen Sie eine aktive Ermittlung aus."],
        "Observed after must be earlier than or equal to observed before.": ["A data de observação posterior deve ser anterior ou igual à data de observação anterior.", "Beobachtet nach muss vor oder gleich Beobachtet vor liegen."],
        "Select the query variants to execute.": ["Selecione as variantes da consulta a executar.", "Wählen Sie die auszuführenden Abfragevarianten aus."],
        "No safe automatic variant was suggested.": ["Não foi sugerida nenhuma variante automática segura.", "Es wurde keine sichere automatische Variante vorgeschlagen."],
        "Enter a main query before requesting variants.": ["Introduza uma consulta principal antes de pedir variantes.", "Geben Sie eine Hauptabfrage ein, bevor Sie Varianten anfordern."],
        "Delete all Synthesix search history and generated result reports? Investigation folders and explicitly saved pages are preserved.": ["Eliminar todo o histórico de pesquisas do Synthesix e os relatórios de resultados gerados? As pastas de investigação e as páginas guardadas explicitamente serão preservadas.", "Den gesamten Synthesix-Suchverlauf und alle erstellten Ergebnisberichte löschen? Ermittlungsordner und ausdrücklich gespeicherte Seiten bleiben erhalten."],
        "Clear history, cookies, cache, and site data from the Synthesix browser profile? Saved sessions will be signed out.": ["Limpar o histórico, os cookies, a cache e os dados de sites do perfil do navegador Synthesix? As sessões guardadas serão terminadas.", "Verlauf, Cookies, Cache und Websitedaten aus dem Synthesix-Browserprofil löschen? Gespeicherte Sitzungen werden abgemeldet."],
        "Remove this page from the investigation? The underlying search observation is preserved.": ["Remover esta página da investigação? A observação de pesquisa subjacente será preservada.", "Diese Seite aus der Ermittlung entfernen? Die zugrunde liegende Suchbeobachtung bleibt erhalten."],
        "Delete this evidence capture and its files?": ["Eliminar esta captura de prova e os respetivos ficheiros?", "Diese Beweisaufnahme und ihre Dateien löschen?"],
        "Stop monitoring this page?": ["Parar de monitorizar esta página?", "Überwachung dieser Seite beenden?"],
        "Delete this extracted entity?": ["Eliminar esta entidade extraída?", "Diese extrahierte Entität löschen?"],
        "Delete this ZeroNeurone export and its files?": ["Eliminar esta exportação ZeroNeurone e os respetivos ficheiros?", "Diesen ZeroNeurone-Export und seine Dateien löschen?"],
        "Checking...": ["A verificar...", "Prüfung..."],
        "The public IP is listed as a known VPN exit node. Detection can be wrong.": ["O IP público está listado como um nó de saída VPN conhecido. A deteção pode estar errada.", "Die öffentliche IP ist als bekannter VPN-Ausgangsknoten gelistet. Die Erkennung kann fehlerhaft sein."],
        "The public IP is not listed as a known VPN exit node. This does not prove that a VPN is off.": ["O IP público não está listado como um nó de saída VPN conhecido. Isto não prova que a VPN esteja desligada.", "Die öffentliche IP ist nicht als bekannter VPN-Ausgangsknoten gelistet. Das beweist nicht, dass kein VPN aktiv ist."],
        "The external VPN check is unavailable or timed out.": ["A verificação VPN externa está indisponível ou excedeu o tempo limite.", "Die externe VPN-Prüfung ist nicht verfügbar oder hat das Zeitlimit überschritten."],
        "VPN status is missing": ["O estado da VPN está em falta", "VPN-Status fehlt"],
        "This report action is invalid.": ["Esta ação do relatório é inválida.", "Diese Berichtsaktion ist ungültig."],
        "Open report": ["Abrir relatório", "Bericht öffnen"],
        "Delete this capture and its local evidence files": ["Eliminar esta captura e os respetivos ficheiros de prova locais", "Diese Aufnahme und ihre lokalen Beweisdateien löschen"],
        "Add or remove this page from favorites": ["Adicionar ou remover esta página dos favoritos", "Diese Seite zu den Favoriten hinzufügen oder daraus entfernen"],
        "Remove this saved page from the investigation": ["Remover esta página guardada da investigação", "Diese gespeicherte Seite aus der Ermittlung entfernen"]
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
