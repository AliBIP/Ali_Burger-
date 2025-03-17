import pandas as pd
from flask import Flask, render_template, request

# Загружаем данные из CSV
gifts_df = pd.read_csv('gifts_data.csv')

# Создаем приложение Flask
app = Flask(__name__)

# Заполняем пропуски в колонке 'image' значением 'default.jpg' и преобразуем в строку
gifts_df['image'] = gifts_df['image'].fillna('default.jpg')  
gifts_df['image'] = gifts_df['image'].astype(str)

@app.route('/')
def home():
    # Получаем уникальные категории
    categories = gifts_df['category'].unique()
    # Преобразуем данные в формат списка словарей
    gifts = gifts_df.to_dict(orient='records')
    # Отправляем данные в шаблон
    return render_template('index.html', categories=categories, gifts=gifts)

@app.route('/filter', methods=['GET'])
def filter_gifts():
    # Получаем выбранную категорию из параметров запроса
    category = request.args.get('category', default=None)

    # Если категория выбрана, фильтруем подарки по категории
    if category:
        filtered_gifts = gifts_df[gifts_df['category'] == category]
    else:
        filtered_gifts = gifts_df

    # Получаем уникальные категории
    categories = gifts_df['category'].unique()
    
    # Отправляем отфильтрованные данные в шаблон
    return render_template('index.html', gifts=filtered_gifts.to_dict(orient='records'), categories=categories)

if __name__ == '__main__':
    # Запуск приложения
    app.run(debug=True)
