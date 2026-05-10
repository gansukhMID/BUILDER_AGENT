# GitHub Issue Mapping — wms-core-template

Epic: #1 - https://github.com/gansukhMID/BUILDER_AGENT/issues/1

Tasks:
- #4: Project Scaffold + db.py          - https://github.com/gansukhMID/BUILDER_AGENT/issues/4
- #8: Core Mixins                        - https://github.com/gansukhMID/BUILDER_AGENT/issues/8
- #10: Location Model + Hierarchy Utils  - https://github.com/gansukhMID/BUILDER_AGENT/issues/10
- #11: Warehouse Model                   - https://github.com/gansukhMID/BUILDER_AGENT/issues/11
- #2: Product Model                      - https://github.com/gansukhMID/BUILDER_AGENT/issues/2
- #5: Lot Model                          - https://github.com/gansukhMID/BUILDER_AGENT/issues/5
- #7: Quant Model                        - https://github.com/gansukhMID/BUILDER_AGENT/issues/7
- #3: PickingType Model                  - https://github.com/gansukhMID/BUILDER_AGENT/issues/3
- #6: Picking Model + StateMachine       - https://github.com/gansukhMID/BUILDER_AGENT/issues/6
- #9: Move + StockRule + Alembic + Tests - https://github.com/gansukhMID/BUILDER_AGENT/issues/9

Dependency graph (real issue numbers):
  #4 → #8 → #10 → #11
            ↘ #2 → #5
                 ↘
                  #7 (needs #10, #2, #5) ← parallel → #3 (needs #11)
                                                              ↓
                                                             #6
                                                              ↓
                                                             #9 (needs #7, #6)

Synced: 2026-05-08T06:27:58Z
Repo: https://github.com/gansukhMID/BUILDER_AGENT
Branch: epic/wms-core-template
