#### Open   
- [ ] Add a new mechanic to the placement test:  'audios->sort-by-[imagesttext]-categories'.
  - [ ] Add to config.py
  - [ ] Investigate what files to change to add the mechanics (e.g. generate_questions.py, adaptive_engine.py, question_renderer.py, etc)
  - [ ] Implement changes in the files
  - [ ] Re-generate questions with new mechanic (use generate_questions.py)
  - [ ] Test the app with new mechanic (I will do it manually)
  Note: New mechanic is when students look at the images which represent categories (eg 'animals', 'toys') and then sort vocabulary items presented as audios into these categories, e.g. audio that says 'cat' to the category presented by the image 'animals'.

- [ ] Make sure debug info is working and showing correctly for each question in the text

- [ ] Implement less abruptness in the test given this feedback: "It still feels a bit too abrupt that we give Level 5 Questions (n9) after Level 3 question n8 while 7 questions before we were placing the student to Level 1."