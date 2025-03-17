import pandas as pd
from flask import Flask, render_template, request

# Чтение CSV файла с подарками
gifts_df = pd.read_csv('gifts_data.csv')


# Инициализация Flask приложения
app = Flask(__name__)

gifts_df['image'] = gifts_df['image'].fillna('default.jpg')  # Если пустое значение, ставим "default.jpg"
gifts_df['image'] = gifts_df['image'].astype(str)

# Пример того, как передать данные в шаблон
@app.route('/')
def home():
    categories = gifts_df['category'].unique()
    gifts = gifts_df.to_dict(orient='records')
    return render_template('index.html', categories=categories, gifts=gifts)
def home():
    # Получаем список категорий из данных
    categories = gifts_df['category'].unique()
    
    # По умолчанию показываем все подарки
    return render_template('index.html', gifts=gifts_df.to_dict(orient='records'), categories=categories)

@app.route('/filter', methods=['GET'])
def filter_gifts():
    category = request.args.get('category', default=None)

    # Если категория выбрана, фильтруем подарки
    if category:
        filtered_gifts = gifts_df[gifts_df['category'] == category]
    else:
        filtered_gifts = gifts_df

    categories = gifts_df['category'].unique()
    
    return render_template('index.html', gifts=filtered_gifts.to_dict(orient='records'), categories=categories)


if __name__ == '__main__':
    app.run(debug=True)
