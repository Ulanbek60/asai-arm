{
    "name": "АСАИ – АРМ",
    "version": "18.0.1.0.0",
    "summary": "Автоматизированное рабочее место оператора (мебельное производство)",
    "category": "Manufacturing/MES",
    "depends": ["base", "web", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",

        "views/arm_task_views.xml",
        "views/arm_master_views.xml",
        "views/scrap_wizard_views.xml",
        "views/block_wizard_views.xml",
        "views/menu.xml",

        "data/arm_data.xml",
    ],
    "demo": ["demo/arm_demo.xml"],
    "assets": {
        "web.assets_backend": [
            "asai_arm/static/src/scss/arm.scss",
        ],
    },
    "application": True,
    "license": "LGPL-3",
}
