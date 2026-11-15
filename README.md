# StudySlope
Our submission to the Women in Engineering (WiE) 2026 Hackathon!

https://devpost.com/software/studyslope

## StudySlope
*A rocker board and game with AI-generated flashcards from your own notes, turning restless energy into learning.*

## Inspiration
About 1 in 21 Canadians, roughly 1.8 million people, have ADHD (CADDAC). Research from UC Davis links fidgeting to better attention in both young people and adults with ADHD, and the Attention Deficit Disorder Association's own guide encourages finding non-distracting ways to fidget.

Yet the focus tools people with ADHD are pointed toward are mostly screen-based. ADDA lists the Forest app, which rewards you with a virtual tree for staying off your phone, but it doesn't involve movement. Foot fidgets do offer movement, but they're passive and separate from studying. In what we found, none of them connect the two.

## What it does
StudySlope is a rocker board paired with a game that turns your study notes into flashcards.

- **Upload** your notes as text or a PDF.
- **Play** by leaning left and right on the board to steer a penguin down the slope, dodging trees and collecting stars.
- **Learn** by collecting 3 snowflakes and answering a flashcard question correctly to turn them into a coin.
- **Take it to class**: without the electronics, the board works as a quiet fidget tool.
Our first users are university students with ADHD, usually aged 18-24, who study independently on a laptop. They choose where and how they study, so they can put a board under their own desk, and they are also the buyer.

We are not claiming StudySlope treats ADHD or improves grades. It's a prototype, and testing whether it helps is our next step.

## How we built it
- **Board**: Cardboard, duct tape, hot glue
- **Sensing**: Arduino ultrasonic distance sensor (reads how much the board tilts)
- **Game**: Coded in python, where tilt of the board, measured by distance sensor, controls the penguin's left and right movement
- **AI**: Groq on the backend turns uploaded notes into flashcards
- **Design choices**: Steering uses only left and right movement, and the game pauses for each question. This is because ADDA cautioned that fidget tools which demand attention can make it harder to concentrate, so we kept the controls simple.

## What's next for StudySlope
- Read-aloud flashcards and multiple languages, for a wider audience
- A game that gets progressively harder
- AI explanations for each flashcard answer
- A spaced repetition algorithm for better study results
- AI that identifies key areas of focus in your notes
- User testing with ADHD learners, measuring quiz accuracy, session length, and self-reported focus

## Sources
- CADDAC, About ADHD: https://caddac.ca/about-adhd/
- UC Davis Health, "Does fidgeting help people with ADHD focus?": https://health.ucdavis.edu/news/headlines/does-fidgeting-help-people-with-adhd-focus-/2024/10
- ADDA, Best ADHD Apps and Tools for Adults: https://add.org/adhd-tools-for-adults/
