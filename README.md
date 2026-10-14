# 西游记后传式剪辑 Skill

把日常动作剪成一本正经的“大决战”：短动作重复、递进放大分镜、关键帧、交替镜像、功夫音效，以及可选的轻／强法术特效。适配宠物、真人日常动作、运动、产品等素材。

这是给 Codex 使用的剪辑技能与特效辅助代码，需要代理分析素材并建立时间线；不是一条命令自动完成所有视频的成片工具。裁切和镜像也不等于真实多机位拍摄。

## 安装

本仓库根目录就是一个 skill 文件夹。以 Codex 默认技能目录为例：

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/alex-ybuild/xiyou-houchuan-edit.git ~/.codex/skills/xiyou-houchuan-edit
```

如果设置了自定义 `CODEX_HOME`，安装到该目录下的 `skills/xiyou-houchuan-edit`。目标目录已存在时，先备份已有版本，勿覆盖自己的修改。若技能列表未刷新，重新打开 Codex 会话。

使用逐帧特效辅助代码时，建议创建独立 Python 环境：

```bash
cd ~/.codex/skills/xiyou-houchuan-edit
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

完整视频剪辑另需环境中已有的 `ffmpeg` / `ffprobe`，或用户指定的可用视频编辑器。Python 辅助代码使用 NumPy 和 Pillow；无需把 OpenCV 作为必装依赖。

## 使用

在 Codex 中给出可访问的视频路径，例如：

```text
用 $xiyou-houchuan-edit 把这个视频剪成西游记后传式效果。
先分析动作，做明显的全景／中景／特写切换、镜像三连和关键帧。
使用强法术档，导出约 15 秒的 MP4，并给我 Before / After 对比版。
素材：/你的路径/input.mp4
```

可选强度：标准剪辑、轻特效、强法术。强法术包括主体描边、光束／闪电、残影、落地光圈和烟尘，随当前素材的事件与主体轨迹适配；不会套用猫咪示例的固定坐标。

想要经典配乐，可以明确指定：

```text
BGM 使用刘欢《我欲成仙》，连续铺底，不随动作回放重启。
使用我提供的可用音源；如果取不到指定音源，说明情况，不用别的音乐冒充。
```

仓库不附歌曲、原剧音频或视频。音源可访问不代表获得公开发布许可；发布版本需自行确认相应权利。素材署名与许可按来源保留。

## 内容

- [SKILL.md](SKILL.md)：动作分析、剪辑语法、声音及交付规则。
- [原剧节奏实测](references/original-rhythm.md)：两段原剧参考、帧数与景别分析；区分观测事实和改编参数。
- [特效与滤镜](references/effects.md)：不同素材的轻／强档设计、归一化坐标和遮罩要求。
- [渲染规则](references/rendering.md)：FFmpeg 时间线、音画同步及导出验证。
- [action_fx.py](scripts/action_fx.py)：遮罩驱动的 Pillow 特效函数。调用方提供主体遮罩、轨迹和事件时机；脚本不自动检测主体，也不生成整条剪辑或声音。

## 更新与验证

Git 安装的版本可在技能目录运行 `git pull --ff-only` 更新。先处理自己的本地修改。

```bash
.venv/bin/python -m unittest discover -s tests -v
```

测试覆盖空遮罩不改画面、特效局部性、遮罩尺寸校验和可重复的闪电效果。它不代替成片的动作节奏与声音检查。

## License

本仓库原创技能文档与辅助代码以 [MIT](LICENSE) 分发。文中链接的第三方素材、歌曲、剧集和音效保留各自权利，不属于本仓库许可范围。
