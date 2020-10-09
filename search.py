from flask import Flask, render_template, request
import pymysql
import logging

app = Flask(__name__)


@app.route('/search')
def search():
	r = render_template('index.html')  # 之前实现的简单搜索页面
	return r


# 点击搜索后，跳转的页面；
@app.route('/result', methods=['GET', 'POST'])  # 如果使用post方法提交，需要声明methods参数
def showResult():
	keyword = request.args.get('searchText')
	print(keyword)

	con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='test')
	cur = con.cursor()
	sql = 'select * from movieTop250 where Rank = %s'
	try:
		cur.execute(sql, keyword)
		movies = cur.fetchall()
		for movie in movies:
			print(movie)
	except Exception as e:
		print(e)
		logging.error(str(e))
		return '搜索失败'
	finally:
		cur.close()

	return render_template('result.html', result=movies)
	# 数据库查询
	# checkList = ....
	# return render_template('result.html', result = checkList) # 将查到的东西进行页面渲染


if __name__ == '__main__':
	app.run(debug=True)
