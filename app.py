import fitz
@app.route("/pdf", methods=["POST"])
def read_pdf():
    file = request.files["file"]
    doc = fitz.open(stream=file.read(), filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"Analyse ce document"},
            {"role":"user","content":text[:15000]}
        ]
    )

    return jsonify({"analysis":response.choices[0].message.content})
@app.route("/vision", methods=["POST"])
def vision():
    image = request.files["image"]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role":"user",
            "content":[
                {"type":"text","text":"Analyse cette image"},
                {"type":"image_url","image_url":{"url":"data:image/jpeg;base64," + image.read().encode("base64")}}
            ]
        }]
    )

    return jsonify({"result":response.choices[0].message.content})
