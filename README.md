# MyNeuro
My NeuroNetwork that designed as my virtual partner

The projetct is still in early development. More features and improvements will be added soon.

# plans
- temporarily use <b><del>deepseek</del> Qwen</b> api for instead of local model for efficiency. ---->√ done
- connect API for dicord bot. temperarily let discord bot to call the API subjectively. ---->√ done
- modify and optimize the chat module for better performance in memory. 

# future plans
- Deploy <b>Qwen-Audio model</b> as main LLM for audio processing.
- Add tools to complete the chat module for wechat.(wechat terminal version get from github repo:)----> (x) no API available for wechat
- transfer to discord chatbot.

# logs
- 2026-1-11: Initial commit with basic structure and README file.
- 2026-1-12: Added client module for AI interaction and test script.
- 2026-1-15: discord library added for bot integration. proxy support added in Discord.env.
- 2026-1-16: Discord bot connectiong test successful with proxy support.
- 2026-1-16: Streamed response handling implemented in AIClient.
- 2026-1-16: LLM has connected to discord bot successfully.