---
type: "query"
date: "2026-06-28T09:23:01.005650+00:00"
question: "Comment Synthesix genere ses rapports ?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["SearchOrchestrator", "generate_html_report", "generate_history_html", "_generate_investigation_page", "generate_investigation_page", "generate_local_search_page", "generate_page_comparison_report", "export_zeroneurone_bundle"]
---

# Q: Comment Synthesix genere ses rapports ?

## Answer

Expanded from original query via vocab: [synthesix, generate, report, reports, history, html, search, result, results, investigation, export, view]. Synthesix genere ses rapports comme fichiers locaux statiques. Recherche: SearchOrchestrator.search agrege/scrore les resultats, appelle utils.generate_html_report, puis add_to_history et generate_history_html. Investigation: main._generate_investigation_page appelle InvestigationService.workspace_payload puis investigations.view.generate_investigation_page, qui ecrit data/investigation_pages/<id>.html. Annexes: investigations.search_view.generate_local_search_page pour archive locale, investigations.monitoring_view.generate_page_comparison_report pour diff surveillance, exports.zeroneurone.export_zeroneurone_bundle pour GraphML/CSV/dossier/manifest. ui.py fournit shell et composants HTML communs.

## Outcome

- Signal: useful

## Source Nodes

- SearchOrchestrator
- generate_html_report
- generate_history_html
- _generate_investigation_page
- generate_investigation_page
- generate_local_search_page
- generate_page_comparison_report
- export_zeroneurone_bundle