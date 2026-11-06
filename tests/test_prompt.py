def test_build_prompt_includes_question_and_type(assistant):
    question = "What type is Gengar?"
    prompt = assistant.build_prompt(question, assistant.search(question))
    assert question in prompt
    assert "ghost" in prompt.split("Context:")[1].lower()
