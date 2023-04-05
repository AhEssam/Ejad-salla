# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import copy
import datetime
import functools
import hashlib
import io
import itertools
import json
import logging
import operator
import os
import re
import sys
import tempfile
import unicodedata
from collections import OrderedDict, defaultdict
from datetime import datetime,timedelta
from urllib import response
import babel.messages.pofile
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from lxml import etree, html
from markupsafe import Markup
from werkzeug.urls import url_encode, url_decode, iri_to_uri

import odoo
import odoo.modules.registry
from odoo.api import call_kw
from odoo.addons.base.models.ir_qweb import render as qweb_render
from odoo.modules import get_resource_path, module
from odoo.tools import html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, float_repr, osutil
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open, file_path
from odoo.tools.safe_eval import safe_eval, time
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security
from odoo import models
import dateutil.parser
import cv2
import numpy as np
import requests
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from email import message
from email.mime import audio
import random
import pickle
# from matplotlib.font_manager import list_fonts
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import json
from tensorflow.keras.models import load_model
from gtts import gTTS
import pprint
from bidi.algorithm import get_display
import speech_recognition as sr
import pyttsx3
#from playsound import playsound
import arabic_reshaper
from pydub import AudioSegment


# nltk.download('punkt')
# nltk.download('wordnet')
# # convert mp3 file to wav
# nltk.download('omw-1.4')
_logger = logging.getLogger(__name__)

CONTENT_MAXAGE = http.STATIC_CACHE_LONG  # menus, translations, static qweb

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

COMMENT_PATTERN = 'Modified by [\s\w\-.]+ from [\s\w\-.]+'


class Salla(http.Controller):
    @http.route('/text/request', type='http',csrf=False , auth="public",methods=['GET'])


    def request_text(self,text, **kw):
        print(text)

        intents  = json.loads(open('/var/www/html/chatbot/python/intent.json').read())

       
        model = load_model('/var/www/html/chatbot/python/ejad_chatbot.h5')
        # return json.dumps({
        # 'message' : text,
        # 'success' : 1
        # })
     
        # return json.dumps({
        # 'message' : 'res',
        # 'success' : 1
        #     })
        # try:
        #     with sr.AudioFile('/var/www/html/chatbot/python/sound.wav') as source:
        #         audio = r.record(source)  # read the entire audio file
        #         MyText = r.recognize_google(audio,language='ar-sa')
        #         message = MyText.lower()
        ints = self.predict_class(text)
        res = self.get_response(ints,intents)
            #     print(res)
        return json.dumps({
        'message' : res[0],
        'tag' : res[1],
        'response' : res[2],
        're' : ints,

        'success' : 1
            })
        # except:
        #         return json.dumps({
        #         'message' : 'لا افهمك ',
        #         'success' : 1
        #             })

     

    @http.route('/customer/add', type='json',csrf=False , auth="public",methods=['POST'])
    def create_customer(self, **kw):
       d = json.loads(request.httprequest.data);
       partner = request.env['res.partner'].sudo()
       salla = request.env['integration.salla'].sudo().search([],limit = 1)
       _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent batch %s',pprint.pformat(d))
       partner_id = partner.create({
                                    'salla_id': d['id'],

                                'name': d['first_name'] + ' ' + d['last_name'],
                                "company_type": 'person',
                                "company_id":salla.company_id.id,
                                "mobile": d['mobile'],
                                "email": d['email'],
                                'image_1920':self.get_salla_image(d['avatar']),


                              
                            })
       if partner_id : 
        return json.dumps({
            'message' : ' create partner success',
            'success' : 1
        })
 
    # Dictionary to JSON Object using dumps() method
    # Return JSON Object
       return json.dumps({
            'message' : 'error create partner',
            'success' : 0
        })
    def clean_up_sentence(self,sentence):
        lemmatizer = WordNetLemmatizer()

        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
        return sentence_words


    def bag_of_words(self,sentence):
        words = pickle.load(open('/var/www/html/chatbot/python/words.pkl','rb'))

        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(words)
        for w in sentence_words:
            for i , word in enumerate(words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)



    def predict_class(self,sentence):


        model = load_model('/var/www/html/chatbot/python/ejad_chatbot.h5')
        classes = pickle.load(open('/var/www/html/chatbot/python/classes.pkl','rb'))

        bow = self.bag_of_words(sentence)
        res = model.predict(np.array([bow]),verbose=0)[0]
        ERROR_THRESHOLD = 0.25
        results = [[i,r] for i , r in enumerate(res) if r > ERROR_THRESHOLD]

        results.sort(key=lambda x: x[1] , reverse=True)
        return_list = []
        for r in results:
            return_list.append({'intent':classes[r[0]] , 'probability':str(r[1])})

        return return_list

    def get_response(self,intent_list , intent_json):
        tag = intent_list[0]['intent']
    #   print('tag %s' % tag)
        list_of_intents  = intent_json['intents']
        result = ''
        response =''
        for i in list_of_intents:

            if i['tag'].lower() == tag:
                response = i['responses'];
                result = random.choice(i['responses'])
                break
        return [result,tag,response ,list_of_intents]


    @http.route('/customer/update', type='json', csrf=False , auth="public")
    def update_customer(self,  **kw):
       d = json.loads(request.httprequest.data);
       partner = request.env['res.partner'].sudo()

       customer = partner.search(
                     [('salla_id', '=', d['id'])])
       if customer:
           customer = customer.write({
             'name': d['first_name'] + ' ' + d['last_name'],
                                "company_type": 'person',
                                "mobile": d['mobile'],
                                "email": d['email'],
                                'image_1920':self.get_salla_image(d['avatar']),

           })
   
           if customer : 
                return json.dumps({
                    'message' : ' update partner success',
                    'success' : 1
                })
 
    # Dictionary to JSON Object using dumps() method
    # Return JSON Object
       return json.dumps({
            'message' : 'error update partner',
            'success' : 0
        })
    def get_salla_image(self,imag_url):
            if not imag_url:
                return ''
            response = requests.get(imag_url)

            url = response.content
            
            imageBase64 = base64.b64encode(url)
            imageBase64 = str(imageBase64)
            imageBase64 = imageBase64[2:]
            imageBase64 = imageBase64[:-1]

            # imageBase64 = imageBase64.rstrip(imageBase64[-1])

            return imageBase64
    @http.route('/product/update', type='json',csrf=False , auth="public",methods=['POST'])
    def update_product(self, **kw):
       product = json.loads(request.httprequest.data);
       _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent batch %s', 'start')
       i = 0
    #    for c in product["taxed_price"]:
    #     i = i +1;
    #    return json.dumps({
    #         'message' : ' create partner success',
    #         'success' :i
    #     })
       ProductTemplate = request.env['product.template'].sudo()
       ProductProduct = request.env['product.product'].sudo()
       ProductAttribute = request.env['product.attribute'].sudo()
       ProductAttributeValue = request.env['product.attribute.value'].sudo()
       ProductTemplateAttributeValue = request.env['product.template.attribute.value'].sudo()
       ProductTemplateAttributeLine = request.env['product.template.attribute.line'].sudo()
       ProductCategory = request.env['product.category'].sudo()

       salla = request.env['integration.salla'].sudo().search([],limit = 1)
       
       product_tmpl_id = ProductTemplate.search(
                     [('salla_id', '=', product['id'])])
                   
       if product_tmpl_id:
            _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent product_tmpl_id %s', product_tmpl_id)

            product_tmpl_id = product_tmpl_id.write({
                            'name': product['name'],
                            'standard_price':product['cost_price'],
                            'list_price':product['price']['amount'],
                     'image_1920':self.get_salla_image(product['main_image']),

                           
                        })
            product_category = ''
            if product['categories']:
                for dic in product['categories']:
                    print('**********cate*****',dic)
                    _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent batch %s', dic)
                    product_category = ProductCategory.search([('salla_id', '=', dic['id'])])
                    if  product_category :
                      product_category = ProductCategory.write({
                                        'parent_id':salla.parent_category_salla.id,
                                        'name': dic['name'],
                                        'salla_id':dic['id']})
                _logger.info('*********************************> %s', product_category)
                # if product_category:
                    # product_tmpl_id.categ_id = product_category.id

            # attribute_ids = []
            # value_ids = []
            #         # choice next product
            # if product['options']:   
            #     for option in product['options']:
            #         attribute_id = ProductAttribute.search([('salla_id', '=', option['id'])])
                        
            #         if not attribute_id:
            #             attribute_id = ProductAttribute.write({'name': option['name'],
            #                                                     'salla_id':option['id']

            #                         })
            #         for value in option['values']: 
                                
            #             value_id = ProductAttributeValue.search([('attribute_id', '=', attribute_id.id), ('name', '=', value['name'])], limit=1)
            #             if not value_id:
            #                     value_id = ProductAttributeValue.write({'name': value['name'], 'attribute_id': attribute_id.id})
            #             value_ids.append(value_id)

            #             ptal_id = ProductTemplateAttributeLine.search([('product_tmpl_id', '=', product_tmpl_id.id), ('attribute_id', '=', attribute_id.id)], limit=1)
            #             if not ptal_id:
            #                 ptal_id = ProductTemplateAttributeLine.write({
            #                             'product_tmpl_id': product_tmpl_id.id,
            #                             'attribute_id': attribute_id.id,
            #                             'value_ids': [(6, 0, [value_id.id])]
            #                         })
            #             else:
            #                 ptal_id.write({'value_ids': [(4, value_id.id)]})

      
       if product_tmpl_id : 
            return json.dumps({
                'message' : ' update product success',
                'success' : 1
            })
    @http.route('/product/details', type='json',csrf=False , auth="public",methods=['POST'])
    def product_data(self, **kw):
       product = json.loads(request.httprequest.data);
       _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent batch %s', product)
       i = 0
 
       ProductTemplate = request.env['product.template'].sudo()
       StockQ = request.env['stock.quant'].sudo()

       product_tmpl_id = ProductTemplate.search(
                     [('salla_id', '=', product['id'])])
       
    #    for c in product["taxed_price"]:
    #     i = i +1;
       if product_tmpl_id:
           stock = StockQ.search([('product_tmpl_id','=',product_tmpl_id.id)])[0]
           if stock:
        
                return json.dumps({
                    "success" : 1,
                            'message' : 'success',
                            'quantity' :stock.quantity,
                            'inventory_quantity' : stock.inventory_quantity,
                            'available_quantity':stock.available_quantity,
                            'on_hand' : stock.on_hand,

                })
           return json.dumps({
                    'message' : 'not found',
                    'success' :0,

                });
       return json.dumps({
                    'message' : 'not found',
                    'success' :0,

                });
    @http.route('/api/products', type='json',csrf=False , auth="public",methods=['POST'])
    def products(self, **kw):
       ProductTemplate = request.env['product.template'].sudo()
       ProductProduct = request.env['product.product'].sudo()
       ProductAttribute = request.env['product.attribute'].sudo()
       ProductAttributeValue = request.env['product.attribute.value'].sudo()
       ProductTemplateAttributeValue = request.env['product.template.attribute.value'].sudo()
       ProductTemplateAttributeLine = request.env['product.template.attribute.line'].sudo()
       ProductCategory = request.env['product.category'].sudo()
       products = [];
       product_temp = ProductTemplate.search([]);
       if product_temp:
            for p in product_temp:

                products.append({
                    "name":p["name"],
                    "standard_price":p["standard_price"]

                })


            return json.dumps({
                'success' :1,
                'data':products

                });
       return json.dumps({
                'message' : 'no products',
                'success' :0,
               

                });

    @http.route('/product/add', type='json',csrf=False , auth="public",methods=['POST'])
    def create_product(self, **kw):
       product = json.loads(request.httprequest.data);
       _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent batch %s', product)
       i = 0
    #    for c in product["taxed_price"]:
    #     i = i +1;
    #    return json.dumps({
    #         'message' : ' create partner success',
    #         'success' :i
    #     })
       ProductTemplate = request.env['product.template'].sudo()
       ProductProduct = request.env['product.product'].sudo()
       ProductAttribute = request.env['product.attribute'].sudo()
       ProductAttributeValue = request.env['product.attribute.value'].sudo()
       ProductTemplateAttributeValue = request.env['product.template.attribute.value'].sudo()
       ProductTemplateAttributeLine = request.env['product.template.attribute.line'].sudo()
       ProductCategory = request.env['product.category'].sudo()
       StockQ = request.env['stock.quant'].sudo()


       salla = request.env['integration.salla'].sudo().search([],limit = 1)
       
       product_tmpl_id = ProductTemplate.search(
                     [('salla_id', '=', product['id'])])
                   
       if not product_tmpl_id:
            product_tmpl_id = ProductTemplate.create({
                            'name': product['name'],
                            'salla_id': product['id'],
                            'detailed_type': 'product',
                            'standard_price':product['cost_price'],
                            'list_price':product['price']['amount'],
                            'image_1920':self.get_salla_image(product['main_image']),
                            'company_id':salla.company_id.id,
                            # 'categ_id': product_category.id,
                        
                            # 'attribute_line_ids': attribute_line_ids
                        })
            stock = StockQ.search([('product_tmpl_id','=',product_tmpl_id.id)])
            # if product['skus']:
            StockQ.inventory_quantity = product['quantity']
            _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent batch %s', product['quantity'])

            product_category = ''
            if product['categories']:
                for dic in product['categories']:
                    print('**********cate*****',dic)
                    _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent batch %s', dic)
                    product_category = ProductCategory.search([('salla_id', '=', dic['id'])])
                    if not product_category :
                      product_category = ProductCategory.create({
                                        'parent_id':salla.parent_category_salla.id,
                                        'name': dic['name'],
                                        'salla_id':dic['id']})
                    
                product_tmpl_id.categ_id = product_category.id

            attribute_ids = []
            value_ids = []
                    # choice next product
            if product['options']:   
                for option in product['options']:
                    attribute_id = ProductAttribute.search([('salla_id', '=', option['id'])])
                        
                    if not attribute_id:
                        attribute_id = ProductAttribute.create({'name': option['name'],
                                                                'salla_id':option['id']

                                    })
                    for value in option['values']: 
                                
                        value_id = ProductAttributeValue.search([('attribute_id', '=', attribute_id.id), ('name', '=', value['name'])], limit=1)
                        if not value_id:
                                value_id = ProductAttributeValue.create({'name': value['name'], 'attribute_id': attribute_id.id})
                        value_ids.append(value_id)

                        ptal_id = ProductTemplateAttributeLine.search([('product_tmpl_id', '=', product_tmpl_id.id), ('attribute_id', '=', attribute_id.id)], limit=1)
                        if not ptal_id:
                            ptal_id = ProductTemplateAttributeLine.create({
                                        'product_tmpl_id': product_tmpl_id.id,
                                        'attribute_id': attribute_id.id,
                                        'value_ids': [(6, 0, [value_id.id])]
                                    })
                        else:
                            ptal_id.write({'value_ids': [(4, value_id.id)]})

       return json.dumps({
                'message' : ' create product success',
                'success' : 1
            })
       if product_tmpl_id : 
            return json.dumps({
                'message' : ' create product success',
                'success' : 1
            })
        
    @http.route('/order/add', type='json',csrf=False , auth="public",methods=['POST'])
    def create_order(self, **kw):

       order = json.loads(request.httprequest.data);
      
       SaleOrder = request.env['sale.order'].sudo()
       SaleOrderLine = request.env['sale.order.line'].sudo()
       ResCurrency = request.env['res.currency'].sudo()
       CrmTeam = request.env['crm.team'].sudo()
       ProductTemplate = request.env['product.template'].sudo()
       ProductProduct = request.env['product.product'].sudo()
       ProductAttribute = request.env['product.attribute'].sudo()
       ProductAttributeValue = request.env['product.attribute.value'].sudo()
       ProductTemplateAttributeValue = request.env['product.template.attribute.value'].sudo()
       ProductTemplateAttributeLine = request.env['product.template.attribute.line'].sudo()
       ProductCategory = request.env['product.category'].sudo()
       ProductPricelist = request.env['product.pricelist'].sudo()
       ProductPricelistItem = request.env['product.pricelist.item'].sudo()
       AccountTax = request.env['account.tax'].sudo()
       salla_integration_id = request.env['integration.salla'].sudo().search( [], limit=1)
       saleorder_id = SaleOrder.search([('salla_id', '=', order['id']), ('salla_integration_id', '=', salla_integration_id.id)], limit=1)
       
       if not saleorder_id:
            partner_id = request.env['res.partner'].sudo().search([('salla_id','=',order['customer']['id'])])
            print("????????????????????>>>>>>>>>",order['status']['slug'])
            if not partner_id:
               partner_id =  request.env['res.partner'].sudo().create({
                                'name': order['customer']['first_name'] + ' ' + order['customer']['last_name'],
                                "company_type": 'person',
                                "mobile":order['customer']['mobile'],
                                "email": order['customer']['email'],
                              

                })
            payment_method = request.env['salla.payment.method'].sudo().search([('name','=',order['payment_method'])])
            if not payment_method:
                        request.env['salla.payment.method'].sudo().create({'name':order['payment_method']})
                        payment_method = request.env['salla.payment.method'].sudo().search([('name','=',order['payment_method'])])

            d =datetime.strptime(str(dateutil.parser.parse(order['date']['date'])),"%Y-%m-%d %H:%M:%S")
            saleorder_id = SaleOrder.create({
                                        'partner_id': partner_id.id,
                                        # 'date_order': ,
                                        "salla_id": order['id'],
                                        "payment_method":payment_method.id,
                                        "salla_integration_id": salla_integration_id.id,
                                        "company_id":salla_integration_id.company_id.id,
                                        "order_t":'salla',
                                        "salla_state":order['status']["slug"],
                                        "salla_order_date":d,
                                        # 'journal_id':salla_integration_id.journal_id.id,
                                       
                                    })
            _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent batch %s', saleorder_id)
                
            for p in order['items']:
                                                
                    product_id = ProductTemplate.search([('salla_id','=',p['product']['id'])] ,limit=1)
                    if not product_id:
                        product_id = ProductTemplate.create({
                                       'name': p['name'],
                                       'salla_id': p['id'],
                                        'type': 'product',
                                        'categ_id': salla_integration_id.parent_category_salla.id,
                        
                            # 'attribute_line_ids': attribute_line_ids
                                                  })
                    product =  ProductProduct.search([('product_tmpl_id','=',product_id.id)] ,limit=1)
                    if product_id.name:
                        name = product_id.name
                                
                    if product:
                      
                        _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> %s', p['amounts']['total_discount'])
                        discount = int(p['amounts']['total_discount']['amount']) 
                        dis_percentage = 0
                        if discount != 0 :
                            dis_percentage = (discount/int(p['amounts']['price_without_tax']['amount']))*100
                        SaleOrderLine.create({
                                        'order_id': saleorder_id.id,
                                        'name': name,
                                        'product_id': product.id,
                                        'product_uom': product.uom_id.id,
                                        'discount':dis_percentage,
                                        'product_uom_qty': p['quantity'],
                                        'price_unit': p['amounts']['price_without_tax']['amount'],
                                        'tax_id':  [(6, 0, [salla_integration_id.tax_id.id])],
                                                        })
            if order['shipping']:              
                delivery_carrier_id = request.env['delivery.carrier'].sudo().search(
                                                         [('name', '=', order['shipping']['company'])])
                delivery_template_id = ''
                if not delivery_carrier_id:
                        delivery_template_id = ProductTemplate.create({
                            'name': order['shipping']['company'],
                            'type': 'service',
                            'company_id':salla_integration_id.company_id.id,
                            'categ_id': request.env.ref('delivery.product_category_deliveries').id,
                            'taxes_id': [(6, 0, [salla_integration_id.tax_id.id])]     })
                else:
                     delivery_template_id = delivery_carrier_id.product_id.product_tmpl_id

                                                    
                delivery_product_id = ProductProduct.search([('product_tmpl_id', '=', delivery_template_id.id)], limit=1)

                delivery_carrier_id = request.env['delivery.carrier'].sudo().create({
                        'name': order['shipping']['company'],
                        'delivery_type': 'fixed',
                        'company_id':salla_integration_id.company_id.id,
                        'product_id': delivery_product_id.id,
                                                })

                if delivery_carrier_id:
                        print(delivery_carrier_id)
                        delivery_carrier_id.product_id.write({'taxes_id': [(6, 0, [salla_integration_id.tax_id.id])]})

                saleorder_id.set_delivery_line(delivery_carrier_id,order['amounts']['shipping_cost']['amount'])
                saleorder_id.write({
                                                  'recompute_delivery_price': False,
                                                   'delivery_message': order['shipping']['company'],
                                                        })
            saleorder_id.salla_state = order['status']['slug']
            if saleorder_id.salla_state == 'under_review':
                       saleorder_id.action_confirm()
            if saleorder_id.salla_state == 'in_progress':
                   if saleorder_id.state!='sale':
                            saleorder_id.action_confirm()
                            saleorder_id.run_create_invoice()
            if saleorder_id.salla_state == 'completed':
                        for invoice in saleorder_id.invoice_ids:
                              invoice.action_post()
            if saleorder_id.salla_state == 'canceled':
                                 saleorder_id.run_cancel()
            return json.dumps({
                'message' : ' create order success',
                'success' : 1
              })
   
    
    @http.route('/order/update', type='json',csrf=False , auth="public",methods=['POST'])
    def update_order(self, s_action=None, db=None, **kw):
       SaleOrder = request.env['sale.order'].sudo()
       SaleOrderLine = request.env['sale.order.line'].sudo()
       ResCurrency = request.env['res.currency'].sudo()
       CrmTeam = request.env['crm.team'].sudo()
       ProductTemplate = request.env['product.template'].sudo()
       ProductProduct = request.env['product.product'].sudo()
       ProductAttribute = request.env['product.attribute'].sudo()
       ProductAttributeValue = request.env['product.attribute.value'].sudo()
       ProductTemplateAttributeValue = request.env['product.template.attribute.value'].sudo()
       ProductTemplateAttributeLine = request.env['product.template.attribute.line'].sudo()
       ProductCategory = request.env['product.category'].sudo()
       ProductPricelist = request.env['product.pricelist'].sudo()
       ProductPricelistItem = request.env['product.pricelist.item'].sudo()
       AccountTax = request.env['account.tax'].sudo()
       salla_integration_id = request.env['integration.salla'].sudo().search( [], limit=1)
       order = json.loads(request.httprequest.data);

      
       saleorder_id = SaleOrder.search([('salla_id', '=', order['id']), ('salla_integration_id', '=', salla_integration_id.id)], limit=1)
       
       if  saleorder_id:
           
            saleorder_id.salla_state = order['order']['status']['slug']
            if saleorder_id.salla_state == 'under_review':
                       saleorder_id.action_confirm()
            if saleorder_id.salla_state == 'in_progress':
                   if saleorder_id.state!='sale':
                            saleorder_id.action_confirm()
                            saleorder_id.run_create_invoice()
            if saleorder_id.salla_state == 'completed':
                        for invoice in saleorder_id.invoice_ids:
                              invoice.action_post()
            if saleorder_id.salla_state == 'canceled':
                    saleorder_id.run_cancel()
            if saleorder_id.salla_state == 'deleted':
                    saleorder_id.run_cancel()
            return json.dumps({
                'message' : '  order updated success',
                'success' : 1
              })
    # @http.route('/order/delete', type='json',csrf=False , auth="public",methods=['POST'])
    # def update_order(self, s_action=None, db=None, **kw):
    #    SaleOrder = request.env['sale.order'].sudo()
    #    SaleOrderLine = request.env['sale.order.line'].sudo()
    #    ResCurrency = request.env['res.currency'].sudo()
    #    CrmTeam = request.env['crm.team'].sudo()
    #    ProductTemplate = request.env['product.template'].sudo()
    #    ProductProduct = request.env['product.product'].sudo()
    #    ProductAttribute = request.env['product.attribute'].sudo()
    #    ProductAttributeValue = request.env['product.attribute.value'].sudo()
    #    ProductTemplateAttributeValue = request.env['product.template.attribute.value'].sudo()
    #    ProductTemplateAttributeLine = request.env['product.template.attribute.line'].sudo()
    #    ProductCategory = request.env['product.category'].sudo()
    #    ProductPricelist = request.env['product.pricelist'].sudo()
    #    ProductPricelistItem = request.env['product.pricelist.item'].sudo()
    #    AccountTax = request.env['account.tax'].sudo()
    #    salla_integration_id = request.env['integration.salla'].sudo().search( [], limit=1)
    #    order = json.loads(request.httprequest.data);
    #    saleorder_id = SaleOrder.search([('salla_id', '=', order['id']), ('salla_integration_id', '=', salla_integration_id.id)], limit=1)
    #    if  saleorder_id:
    #         saleorder_id.run_cancel()
    #         # saleorder_id.unlink()
    #         return json.dumps({
    #             'message' : '  order updated success',
    #             'success' : 1
    #           })
    
    
    
