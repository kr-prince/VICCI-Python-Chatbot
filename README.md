# VICCI-Python-Chatbot

Vicci - Very Intelligent Covid Chat Interface. A chatbot made using Python and classical Machine Learning to answer basic COVID-19 related queries like definition, symptoms, spreading, treatment, methods to protect, long-term effects, testing.

## Setup

1. ``` git clone https://github.com/kr-prince/VICCI-Python-Chatbot.git``` or simply download the folder locally as zip, and extract it
2. ``` cd VICCI-Python-Chatbot ```
3. Download GloVe vectors from [this](https://nlp.stanford.edu/data/glove.6B.zip) link. Unzip and keep the file **glove.6B.100d.txt** in **models** folder.
4. Run ``` conda env create -f environment.yml ```
5. Run ``` conda activate vicciEnv ```
6. Run the bot flask application by ``` python vicci-main.py ```
7. If you face any issues with the existing models, you can train afresh by deleting the **.joblib** files in the **models** folder and run ``` python botmodel.py ``` 

You can find the detailed blogs for this project here - [Part 1](https://nphard12.medium.com/vicci-very-intelligent-covid-chat-interface-70b9eaeea1ae), [Part 2](https://nphard12.medium.com/meet-vicci-very-intelligent-covid-chat-interface-2-6ef26754b702)

Please feel free to add and contribute 

## Application Preview

![Image1](https://github.com/kr-prince/VICCI-Python-Chatbot/blob/main/static/screenshots/shot1.png)
![Image2](https://github.com/kr-prince/VICCI-Python-Chatbot/blob/main/static/screenshots/shot2.png)
![Image3](https://github.com/kr-prince/VICCI-Python-Chatbot/blob/main/static/screenshots/shot3.png)
![Image4](https://github.com/kr-prince/VICCI-Python-Chatbot/blob/main/static/screenshots/shot4.png)
![Image5](https://github.com/kr-prince/VICCI-Python-Chatbot/blob/main/static/screenshots/shot5.png)
