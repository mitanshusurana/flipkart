from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    avg_price=0
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            logging.info(len(bigboxes))
            reviews = []
            
            for box in bigboxes:
                try:
                    logging.info("https://www.flipkart.com" + box.div.div.div.a['href'])
                    prodRes = requests.get("https://www.flipkart.com" + box.div.div.div.a['href'])
                    prodRes.encoding='utf-8'
                    prod_html = bs(prodRes.text, "html.parser")
                    print(prod_html)
                    prod_price=prod_html.find_all('div', {'class':"_30jeq3 _16Jk6d"})[0].text
                    prod_name=prod_html.find_all('span', {'class':"B_NuCI"})[0].text
                    logging.info(prod_price)
                    logging.info(prod_name)

                    commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

                    filename = searchString + ".csv"
                    fw = open(filename, "a")
                    headers = "Product, Customer Name, Rating, Heading, Comment \n"
                    fw.write(headers)
                    
                    for commentbox in commentboxes:
                        try:
                            #name.encode(encoding='utf-8')
                            name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                        except:
                            logging.info("name")

                        try:
                            #rating.encode(encoding='utf-8')
                            rating = commentbox.div.div.div.div.text


                        except:
                            rating = 'No Rating'
                            logging.info("rating")

                        try:
                            #commentHead.encode(encoding='utf-8')
                            commentHead = commentbox.div.div.div.p.text

                        except:
                            commentHead = 'No Comment Heading'
                            logging.info(commentHead)
                        try:
                            comtag = commentbox.div.div.find_all('div', {'class': ''})
                            #custComment.encode(encoding='utf-8')
                            custComment = comtag[0].div.text
                        except Exception as e:
                            logging.info(e)

                        reviews.append({"Product name": prod_name, "Product price": prod_price, "Name": name, "Rating": rating, "CommentHead": commentHead,
                                "Comment": custComment})
                                
                        fw.write(prod_name+","+prod_price+","+name+","+rating+","+commentHead+","+custComment+"\n")
                    logging.info("log my final result {}".format(reviews))

                    
                    client = pymongo.MongoClient("mongodb+srv://pwskills:pwskills@cluster0.ln0bt5m.mongodb.net/?retryWrites=true&w=majority")
                    db =client['scrapper_eng_pwskills']
                    coll_pw_eng = db['scraper_pwskills_eng']
                    coll_pw_eng.insert_many(reviews)

                except Exception as e:
                        logging.info(e)
                         
            logging.info(reviews)
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
                        logging.info(e)
                        return 'something is wrong'
            # return render_template('results.html')

        else:
                return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
