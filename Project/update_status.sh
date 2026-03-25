#!/bin/bash

# 此脚本用于批量更新项目详情页面的状态标识
# 将状态从独立区域移到card-actions底部左侧

echo "开始批量更新状态标识位置..."

# 定义状态模板
SUCCESS_STATUS='<div class="badge badge-success badge-sm gap-1">
                                    <i class="ri-check-circle-fill"></i>
                                    已完成
                                </div>'

PROGRESS_STATUS='<div class="badge badge-warning badge-sm gap-1">
                                    <span class="loading loading-spinner loading-xs"></span>
                                    生成中 {{PERCENT}}%
                                </div>'

FAILED_STATUS='<div class="tooltip tooltip-error tooltip-top" data-tip="{{REASON}}">
                                    <div class="badge badge-error badge-sm gap-1">
                                        <i class="ri-error-warning-fill"></i>
                                        生成失败
                                    </div>
                                </div>'

echo "状态模板已定义"
echo "需要手动更新以下文件:"
echo "1. project-detail-goods.html (4张卡片)"
echo "2. project-detail-fusion.html (6张卡片)"
echo "3. project-detail-video.html (6张卡片)"  
echo "4. project-detail-tts.html (6张卡片)"
