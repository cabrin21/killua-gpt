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
