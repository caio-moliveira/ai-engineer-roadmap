import os
from openai import AsyncOpenAI
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(title="AI API")

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/generate")
async def generate_text():
    try:
        completion = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": request.prompt}],
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

