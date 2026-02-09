# Principles of backend designing

written by **n1ghts4kura** on 2026/02/09 - 20:00

| 目录 	| 2026/02/09 - 20:00 |
|---	|---	|
| 文件结构 | [File Structure](https://github.com/EOR-Team/ufc-2026/wiki/%E8%A7%84%E8%8C%83-%E5%90%8E%E7%AB%AF%E8%AE%BE%E8%AE%A1#file-structure) |
| ---- 路由 | [Routing](https://github.com/EOR-Team/ufc-2026/wiki/%E8%A7%84%E8%8C%83-%E5%90%8E%E7%AB%AF%E8%AE%BE%E8%AE%A1#about-routing)  	|
| ---- 配置 | [Configuration](https://github.com/EOR-Team/ufc-2026/wiki/%E8%A7%84%E8%8C%83-%E5%90%8E%E7%AB%AF%E8%AE%BE%E8%AE%A1#about-configuration) 	|
| ---- 文档 | [Documentation](https://github.com/EOR-Team/ufc-2026/wiki/%E8%A7%84%E8%8C%83-%E5%90%8E%E7%AB%AF%E8%AE%BE%E8%AE%A1#about-documentation) 	|
| ---- 测试 | [Testing](https://github.com/EOR-Team/ufc-2026/wiki/%E8%A7%84%E8%8C%83-%E5%90%8E%E7%AB%AF%E8%AE%BE%E8%AE%A1#about-testing)  	|
| ---- `.env` 文件 | [Environment Variables](https://github.com/EOR-Team/ufc-2026/wiki/%E8%A7%84%E8%8C%83-%E5%90%8E%E7%AB%AF%E8%AE%BE%E8%AE%A1#about-env-file)  	|
| **Vibe-Coding** | [Vibe-Coding](https://github.com/EOR-Team/ufc-2026/wiki/%E8%A7%84%E8%8C%83-%E5%90%8E%E7%AB%AF%E8%AE%BE%E8%AE%A1#vibe-coding) |

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


### About `Configuration`

> 说实话这一部分我前面两天没有怎么做好。

#### `general.py`

在 `config/general.py` 中存放一些全局配置选项、或者说常量定义。

比如说 `BACKEND_ROOT_DIR` 就是一个**全局性的**常量定义（在你的功能模块和我的里面都可以直接使用）。这样我在实际逻辑中如果遇到多次引用直接导入 `from src.config.general import BACKEND_ROOT_DIR` 就行了。如果发现出了问题也能很快的定位到配置文件具体位置进行修改。不然的话到时候你写了好几条路径要是出了问题排查起来就很麻烦了。用AI也没多好使。

再比如 `OFFLINE_MODEL_CTX_LEN` 就是一个**全局性的**配置选项。不赘述了感觉没啥好说的。

#### `<feature>.py`

这些配置文件都是针对某个具体功能模块的配置选项进行存放的。就不赘述了，喜欢咋搞咋搞。

### About `Documentation`

在 `docs/` 目录下存放一些设计文档、接口文档、使用文档之类的东西。方便后续维护和开发。我的建议是：在**VSCode**中编写好文档之后再上传到 **GitHub Wiki** 上面去。

**不要用AI写文档！**

具体写啥和命名就不做具体要求了，要是文档多到一定数量的话再说吧。

>  不过一般到这个时候文档就很难管理了。

### About `Testing`

在 `src/test/` 目录下存放一些测试脚本，用于对各个功能模块进行单元测试或者集成测试。

没啥具体要求，因为我自己不太用自动化的测试框架工具。如果你想用你也可以在 `requirements.txt` 中添加相应的依赖包，然后自己测试。没毛。

我一般都是直接在这里面写几个直接调用功能模块的脚本，然后运行看看结果对不对。

如果涉及到测试后端路由功能的话，我也习惯用 `Postman` 这种软件或者直接用浏览器来测试。你喜欢用啥就用啥。

### About `.env file` 

这个 `python-dotenv` 库会自动加载项目根目录下的 `.env` 文件中的环境变量到 `os.environ` 中。所以你可以在这个文件中存放一些敏感信息（比如 API Key 之类的东西），然后在代码中通过 `os.environ.get("ENV_VAR_NAME")` 来获取对应的值。

就像我说的那样如果你的`sk-xxx`秘钥直接写进代码里的话，GitHub也会不让你push的。所以你得用这种方式来存放这些敏感信息。你在`.py`代码里面留空，等实际使用再填入的复杂程度和这个其实没区别，但这个模块化程度更高一点，所以我爱用这个。

### About specific features

在具体功能设计中，这样组织文件结构:

先起一个**相对简短**的名字作为功能模块的文件夹名称，就像现在已经有了的 `map/` 一样。

然后在里面怎么组织文件就看具体功能需求了。反正这个也没啥具体要求感觉。你只要能做到**文件结构清晰**, **能让别人看懂**, **方便后续维护和扩展**就行了。

### About general features

对于一些通用的功能模块，比如说简单的日志系统，可以就像现在的 `logger.py` 和 `utils.py` 一样，直接放在 `src/` 目录下就行了。

如果到时候这样的通用功能多了，再专门起一个 `common/` 目录来存放这些通用功能。现在应该还不需要。

## Vibe-Coding

对于模型的选择，我推荐**架构新**但是**日期不新**的模型，比如说最老牌的 `Claude Sonnet 4.5` 这样的模型，因为这些模型经过了时间的考验，有较多使用者。像新的 `GPT-5.2-Codex` 这种模型虽然架构新、评分高，但是**日期太新**，暂时而言使用的量还不够大，对于模型而言训练数据还不够充分，可能反过来还没有老模型好用。

在使用 `VSCode Copilot` 写代码之前，我建议先新建对话，然后用**最好的**模型（评选标准如上），点一遍 `Generate Agent Instructions` 按钮，让他把项目看了一遍之后，你再专门让他生成一份 `docs/` 目录下的设计文档的阅读总结，这样他对一些规范啊啥的都能更明确一点点。

当然，我不是特别建议在这个项目中进行 **Vibe-Coding**，因为这个项目涉及到的 LLM 相关内容感觉上还是比较多的。AI还是比较擅长于 **Web 前后端** 项目中。当然你要用我也拦不住。 lol
