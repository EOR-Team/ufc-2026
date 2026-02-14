# Principles of backend designing

written by **n1ghts4kura** on 2026/02/10 - 22:30

| 目录 	| Links |
|---	|---	|
| 文件结构 | [File Structure](#file-structure) |
| ---- 路由 | [Routing](#about-routing)  	|
| ---- 配置 | [Configuration](#about-configuration) 	|
| ---- 文档 | [Documentation](#about-documentation) 	|
| ---- 测试 | [Testing](#about-testing)  	|
| ---- `.env` 文件 | [Environment Variables](#about-env-file)  	|
| ---- 具体功能 | [Specific Features](#about-specific-features)  	|
| ---- 通用功能 | [General Features](#about-general-features)  	|
| **Vibe-Coding** | [Vibe-Coding](#vibe-coding) |
| **LLM** | [LLM Features](#about-llm-feature) |
| ---- 在线 LLM | [Online LLM](#online-llm-using-openai-agents-lib) |
| ---- 离线 LLM | [Offline LLM](#offline-llm) | 

---

## File Structure

### About `Routing`

在`src/`目录下存放一个`router/`目录，用于专门管理你的接口以及他们的路由规则。

> 提前声明: 我在 `src/router/__init__.py` 中定义了 `api_router` 变量，所以在具体路由的编辑中，你应该引用这个变量作为当级 router 的父 router。

一个好的文件结构案例长这个样子:

```plain
src/router/
	__init__.py
	server_status.py
	
	navigator/
		__init__.py
		chat.py
		generate_map.py		
```

他对应的实际路由结构长这个样子:

```plain
/api
	/server_status
	/chat
		/ stage1?arg1=....&arg2=...
		/ stage2?arg1=...
	/generate_map
		/way1
		/way2
```

> 提醒: 在 FastAPI 中，定义路由时后方加不加`/`字符是有实际意义区别的，尽管并不是很大。

在这个案例中，对于  `/server_status` 这种返回服务器当前……状态的 **功能比较简单的路由，可以直接用一个文件来定义它。

> `server_status.py`大概长这个样子:
> ```python
> # router/server_status.py
> 
> import json
> 
> from src.router import api_router
> 
> 
> @api_router.get("/server_status")
> def get_server_status():
> 	return {
> 		...
> 	}
> ```
> 其中第一行声明文件位置与名称防止 Vibe-Coding 中意外发生。（不好笑我试过错改别的文件。）  
> 标准库导入与项目内库导入相隔一行  
> 导入部分代码与实际逻辑代码相隔两行  
> 不同函数、类之间相隔两行  
> 串场了。好像不应该写这个里的。  
> 

对于`/chat`这种里面还套着第三级内容的路由，如果实现比较复杂，可以将其逻辑拆分成不同的模块，在`/chat/__init__.py`中添加一个`chat_router = APIRouter(prefix="chat")`变量，然后在第三极路由中通过装饰器构建路由。

对于`/generate_map`这种同为套着第三级内容的路由，他的实现就相对简单，这个时候就可以在一个文件内打包好所有内容。当然，在`generate_map.py`中同样要定义一个`generate_map_router = APIRouter(prefix="generate_map")`变量，然后引用这个变量通过装饰器构建路由。

---

### About `LLM`

> 这一部分移步到下文 [`About LLM features`](https://github.com/EOR-Team/ufc-2026/wiki/%E8%A7%84%E8%8C%83-%E5%90%8E%E7%AB%AF%E8%AE%BE%E8%AE%A#about-llm-features) 一块讲完。

---

### About `Configuration`

> 说实话这一部分我前面两天没有怎么做好。

#### `general.py`

在 `config/general.py` 中存放一些全局配置选项、或者说常量定义。

比如说 `BACKEND_ROOT_DIR` 就是一个**全局性的**常量定义（在你的功能模块和我的里面都可以直接使用）。这样我在实际逻辑中如果遇到多次引用直接导入 `from src.config.general import BACKEND_ROOT_DIR` 就行了。如果发现出了问题也能很快的定位到配置文件具体位置进行修改。不然的话到时候你写了好几条路径要是出了问题排查起来就很麻烦了。用AI也没多好使。

再比如 `OFFLINE_MODEL_CTX_LEN` 就是一个**全局性的**配置选项。不赘述了感觉没啥好说的。

#### `<feature>.py`

这些配置文件都是针对某个具体功能模块的配置选项进行存放的。就不赘述了，喜欢咋搞咋搞。

---

### About `Documentation`

在 `docs/` 目录下存放一些设计文档、接口文档、使用文档之类的东西。方便后续维护和开发。我的建议是：在**VSCode**中编写好文档之后再上传到 **GitHub Wiki** 上面去。

**不要用AI写文档！**

具体写啥和命名就不做具体要求了，要是文档多到一定数量的话再说吧。

>  不过一般到这个时候文档就很难管理了。

---

### About `Testing`

在 `src/test/` 目录下存放一些测试脚本，用于对各个功能模块进行单元测试或者集成测试。

没啥具体要求，因为我自己不太用自动化的测试框架工具。如果你想用你也可以在 `requirements.txt` 中添加相应的依赖包，然后自己测试。没毛。

我一般都是直接在这里面写几个直接调用功能模块的脚本，然后运行看看结果对不对。

如果涉及到测试后端路由功能的话，我也习惯用 `Postman` 这种软件或者直接用浏览器来测试。你喜欢用啥就用啥。

---

### About `.env file` 

这个 `python-dotenv` 库会自动加载项目根目录下的 `.env` 文件中的环境变量到 `os.environ` 中。所以你可以在这个文件中存放一些敏感信息（比如 API Key 之类的东西），然后在代码中通过 `os.environ.get("ENV_VAR_NAME")` 来获取对应的值。

就像我说的那样如果你的`sk-xxx`秘钥直接写进代码里的话，GitHub也会不让你push的。所以你得用这种方式来存放这些敏感信息。你在`.py`代码里面留空，等实际使用再填入的复杂程度和这个其实没区别，但这个模块化程度更高一点，所以我爱用这个。

---

### About specific features

在具体功能设计中，这样组织文件结构:

先起一个**相对简短**的名字作为功能模块的文件夹名称，就像现在已经有了的 `map/` 一样。

然后在里面怎么组织文件就看具体功能需求了。反正这个也没啥具体要求感觉。你只要能做到**文件结构清晰**, **能让别人看懂**, **方便后续维护和扩展**就行了。

---

### About general features

对于一些通用的功能模块，比如说简单的日志系统，可以就像现在的 `logger.py` 和 `utils.py` 一样，直接放在 `src/` 目录下就行了。

如果到时候这样的通用功能多了，再专门起一个 `common/` 目录来存放这些通用功能。现在应该还不需要。

---

## Vibe-Coding

对于模型的选择，我推荐**架构新**但是**日期不新**的模型，比如说最老牌的 `Claude Sonnet 4.5` 这样的模型，因为这些模型经过了时间的考验，有较多使用者。像新的 `GPT-5.2-Codex` 这种模型虽然架构新、评分高，但是**日期太新**，暂时而言使用的量还不够大，对于模型而言训练数据还不够充分，可能反过来还没有老模型好用。

在使用 `VSCode Copilot` 写代码之前，我建议先新建对话，然后用**最好的**模型（评选标准如上），点一遍 `Generate Agent Instructions` 按钮，让他把项目看了一遍之后，你再专门让他生成一份 `docs/` 目录下的设计文档的阅读总结，这样他对一些规范啊啥的都能更明确一点点。

当然，我不是特别建议在这个项目中进行 **Vibe-Coding**，因为这个项目涉及到的 LLM 相关内容感觉上还是比较多的。AI还是比较擅长于 **Web 前后端** 项目中。当然你要用我也拦不住。 lol

---

## About `LLM feature`

关于 LLM 相关功能模块的设计，我们将其分为离线LLM推理与在线LLM推理两个部分来进行说明。

### Online LLM (using `openai-agents` lib)

这一部分，我使用曾经写的项目 [`refbook backend - agent_planner`](https://github.com/n1ghts4kura/refbook-backend-advx25/tree/main/agent_planner) 中的 `agent_planner`智能体来举例子说明如何组织文件结构:

```plain
agent_planner/
	__init__.py
	config.py
	general.py
	plan_generator.py
	plan_describer.py
	step_generator.py
	workflow.py
```

`agent_planner`的功能，根据目前用户已经生成或导入好了的参考书内容、以及用户自己的一些要求，为用户生成一个针对这些参考书的学习计划安排。

我将**生成学习计划安排**这一个大的任务分解为了**3个部分**以进行**多 agent 编码与协调**:

- `plan_describer.py`
这一个 agent 的任务是 **解读**: 他先去获取
	1.当前有哪一些教科书  
	2.用户的所有要求的描述  
作为自身输入，输出 *学习计划的名字* 以及 *对学习计划执行细节的详细描述*。
这里的输出会传导到下一个 agent，作为下一个 agent 的输入。

- `step_generator.py`
这个 agent 的任务是 **具象化**: 他会将上面 *对学习计划执行细节的详细描述* 的这一条信息再具体化，具体为执行学习计划的一条条任务清单。
这里的输出会传导到下一个 agent ，作为下一个 agent 的输入。

- `plan_generator.py`
这个 agent 的任务就挺笼统的了，就是将上面的结构化JSON信息诠释为人类易读的文字，就像计划书一样。这个 agent 的输出就是最终的输出了。

你可以按照这样的方法论来思考一下怎么组织你的代码。

> 提醒: 限于**当前没有进行BPU算子编码**的阻碍，你还是要考虑一下本地模型运行的速度的。当然后面我有空了也会去先把CPU推理优化了。

> 你可能会发现我好像没有说 `workflow.py` 是干嘛的。往后看就好了。

---

对于具体的文件内容设计 & 文件结构设计，我推荐你这么干以明确代码结构:

1. 像我上面举的三个例子一样，将 *对 agent 的定义* 单独写在一个文件里面。如果你想使用 **多 agent**，那我还建议加上一个**公共上下文** (*在 `general.py` 中*) 的变量，这样能让所有 agent 明确整体功能的任务，一定程度上可以优化到他的最终输出使他更**切题**。
具体的文件内容结构你可以参考这样子：（只对具体 agent 举例子了。你看旧项目代码去吧）
> ```python
> # xxx_agent.py
> # xxxxxxxxxxxx
> #
> 
> from agent import Agent, ModelSetting, Runner
> # 此处省略导入 ...
> from src.llm.online.model import online_model
> # 导入已经配置好了的在线推理模型！！！不然会报错的！！我已经调整好了设置！！
>
>
> _instructions = """
> <|im_start|>system
> # 这里写背景信息、输入/输出的预期格式、对他的要求、等等。
> # 看旧项目代码你就懂了。
> <|im_end|>
> """
>
> _prompt_ = f"""
> <|im_start|>user
> # 这里写输入
> <|im_end|>
> <|im_start|>assistant    # 留这一行的目的是:
>                          # 利用LLM本质上是**续写机器**的特性，
>                          # 让他续写助手的输出。
>                          # 大概这么个意思。
> """
>
> xxx_agent = Agent(
>     name = "xxxx", # 这里写明白一个概括性的名字作为上下文
> 	  instructions = _instructions,
>     model = online_model # 用配置好了的在线模型
>     model_settings = ModelSetting(....)
> )
>
>
> async def get_xxxxx(arg1, arg2) -> XXXType:
>     return await Runner().run_await(agent, .......)
>     # 这里使用 await 的原因是：
>     # FastAPI 的路由机制 对 async 的路由 function 有优化。
>     # 这个 agent 输出是肯定要嵌入到 HTTP Response 中的嘛，
>     # 刚好 `openai-agents` 也有 async function，就用了。
>     # 这个我是真的不太明白背后的原理。你得自己查资料。我只是公式化的用了一下。
> ```

2. 在 `workflow.py` 文件中声明你的具体逻辑，将上面的各个 agent 底下的 `get_xxx()` 函数串联起来，形成一个完整的工作流 (workflow)。就像我那个旧项目干的一样。
最后导出一个 `run_workflow()` 函数，这个函数会被路由调用，返回路由所需要的数据，这样就完成了一个完整的功能模块。

---

### Offline LLM 

> 这个我还没决定好。你可以看一下下面有啥，然后都试一回，喜欢哪个用那个。

你可以引用 `src/llm/offline/model.py` 中的 `offline_model` 变量，作为 Agent 类构造函数的一个参数，这样他就会自动使用 启动后端服务器时附带启动的 `llama-cpp-python[server]` 中加载好的模型了。（这个模型是在 `src/config/general.py` 中 用字面量选择的，和隔壁 `online/model.py` 不太一样。）

当然，理论上来说这么做有**非常大的弊端**，也就是我一直在疑虑的问题:

使用 `openai-agents` 框架的好处，就是别人已经给你写好了很多预设规范了，这样大模型才能**更听你的话**去工作。但是加载更长的上下文就意味着更长的推理时间，这也就是为什么我在 2026/02/09 时测试出了 280s 的推理时间。显然这个推理时间非常不达标，等到后面我们再回来优化看看能不能救救。

如果你想要**自定义程度更高**，**推理速度加快**，那我推荐你直接用 `llama-cpp-python` 这个库 （就是我一开始提到的库）来推理。你可以使用里面的 **对话补全 (chat completions)** 功能来实现交互（上下文和循环交互当然还是自己组织），也可以使用更加底层的 **文本补全 (text completions)** 功能来实现更加灵活的交互逻辑。

> Docs: [Docs](https://llama-cpp-python.readthedocs.io/en/latest/#high-level-api)
> `Llama()()` 方法实际上就是 *text completions* 功能的封装。
> `Llama().create_chat_completion()` 方法实际上就是 *chat completions* 功能的封装。

这个方法有一个很大的比较，也就是 `openai-agents` 框架的优点: 使用这种比较底层的所谓 *High-Level API*时，你得自己加上 `<|im_start|>` 等 **各种 prompt**技巧，很多时候这些技巧别谈数量之多能不能学会，就连获取都有点困难。（个人感觉。要不是 不知道哪天看到了 `<|im_start|>` 这种**内嵌在模型训练时的** token 使用，……后面没话说了。）

