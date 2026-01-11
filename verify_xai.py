import os
# Mock xAI key if not present, just for initialization check
if 'XAI_API_KEY' not in os.environ:
    os.environ['XAI_API_KEY'] = 'sk-mock-xai-key'
if 'OPENAI_API_KEY' not in os.environ:
    os.environ['OPENAI_API_KEY'] = 'sk-mock-openai-key'

try:
    from utils import setup_llms
    insights, translate = setup_llms()
    if insights and translate:
        print('LLM init OK')
    else:
        print('LLM init FAILED (returned None)')
except Exception as e:
    print(f'LLM init ERROR: {e}')
