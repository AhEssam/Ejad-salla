# -*- coding: utf-8 -*-
import requests
from requests.structures import CaseInsensitiveDict
from odoo import models, fields, api, _
import sys
import json
import logging
import time
import subprocess
import urllib.parse 
# import Salla
from oauthlib.oauth2 import WebApplicationClient
import webbrowser
from odoo.exceptions import UserError, ValidationError


class integration_with_salla(models.Model):
    _name = 'integration.salla'
    _description = 'integration_with_salla.integration_with_salla'

    url = fields.Char()
    token = fields.Char()
    result = fields.Text()
    authorize_url = fields.Char()
    token_url = fields.Char()
    callback_uri= fields.Char()
    client_id = fields.Char()
    client_secret = fields.Char()
    authorization_code = fields.Char()
    refresh_token = fields.Char()
    parent_category_salla = fields.Many2one('product.category')
    uom_id = fields.Many2one('uom.uom')
    tax_id = fields.Many2one('account.tax')
    company_id = fields.Many2one('res.company',string="Company")


    def get_token(self):
        for rec in self:
               if rec.authorization_code:
                        headers = {
                                    'Content-Type': 'application/x-www-form-urlencoded'
                                    }

                        pam={
                                'grant_type': 'authorization_code',
                                'code': rec.authorization_code,
                                # 'scope':'offline_access',
                                'client_id': rec.client_id,
                                'client_secret': rec.client_secret,
                                'redirect_uri': rec.callback_uri
                            }
                        # pam = urllib.parse.urlencode(pam)
                        response = requests.request('POST',
                            rec.token_url,
                            headers=headers,
                            data=pam
                            )
                        
                        if response.status_code == 200:
                            print("&&&&&&&&&&&&&&&&&&&&&new&&&&&&&&&&&#########",'////',response)
                            temp =  response.json()
                            rec.token = ''
                            rec.refresh_token = ''
                            rec.authorization_code = ''
                            rec.token = temp['access_token']
                            rec.refresh_token = temp['refresh_token']
                        else:
                            raise ValidationError(_('please check authorization code '))



               else:
                      raise ValidationError(_('the period'))

    def authorization_get(self):
         for rec in self:   
            CLIENT_ID = "86979270a0f231bd11906da8032575f3"
            CLIENT_SECRET = "7b5c991ef4dc902b9e9650acce885051"
            client = WebApplicationClient(rec.client_id)
            REDIRECT_URI = 'https://localhost:8069'
            AUTHORIZE_URL = "https://accounts.salla.sa/oauth2/auth"
            ACCESS_TOKEN_URL = "https://accounts.salla.sa/oauth2/token"
            url = client.prepare_request_uri(
            rec.authorize_url,
            redirect_uri = rec.callback_uri,
            scope = ['offline_access'],
            state = '12345678'

               )
            webbrowser.open(url, new=2)
           
            # session = requests.Session()

            # login_data = {
            #                 'email': 'm.ali@ejad.sa',
            #                 'password': '123123',
            #                 'submit': 'login',
            #                 }
            # form_content = ''
            # with session as c:
            #     t = c.post( url, data = login_data )
            #     form_content = c.get( url )
            # r = requests.get(AUTHORIZE_URL % urlencode(authorization_code_req),
            #        allow_redirects=False)
            # print("<<<<<<<<<<<<<<",url,'/////////','!!!!!!!!!')
            # data = client.prepare_request_body(
            # # code = 'Uih2nYpb4nJ3kOURrN3IjjVVDlb80NpcVSxokkCUaz4.vtclB8tUNVWuWh_Ri9zhJukQ_Z8J98dC6a5XEC3NqeE',
            # # redirect_uri = 'https://localhost:8069',
            # client_id = CLIENT_ID,
            # client_secret = CLIENT_SECRET,
            # # grant_type = 'authorization_code',
            # code = 'xyCLpO-obQf55AGECCdYlz1q530mDtlaAI-__D2IkJE.jLc01iyZoYbGCyr3N54WHQuPmVGGXKngBbQD1NKum_8',


            # )
            # print("^^^^^^^^^^^^^^^^^6666666",data)
            # headers = {
            #              'Content-Type': 'application/x-www-form-urlencoded'
            #             }

            # pam={
            #         'grant_type': 'authorization_code',
            #         'code': 'xyCLpO-obQf55AGECCdYlz1q530mDtlaAI-__D2IkJE.jLc01iyZoYbGCyr3N54WHQuPmVGGXKngBbQD1NKum_8',
            #         # 'scope':'offline_access',
            #         'client_id': CLIENT_ID,
            #         'client_secret': CLIENT_SECRET,
            #         'redirect_uri': REDIRECT_URI
            #     }
            # # pam = urllib.parse.urlencode(pam)
            # response = requests.request('POST',
            #     ACCESS_TOKEN_URL,
            #     headers=headers,
            #     data=pam
            # )
            # print("&&&&&&&&&&&&&&&&&&&&&new&&&&&&&&&&&#########",'////',response)

    def link(self):
        for rec in self:
  

            myToken = 'Bearer c2TKctNWLvYmAys4SLC_oQpSRpTNKv4hV3UZywsqy9I.etp5cnWkVJU76BLR6ajKmeA1l7E-xG-rXGkiofbzCjs'
            myUrl = 'https://api.salla.dev/admin/v2/orders/1345295632'
            head = {"Accept":"application/json",
            'Authorization': 'token {}'.format('Bearer '+rec.token)}
            response = requests.get(rec.url, headers=head)

            if response.status_code == 200:
                 print(response.json())
                 rec.result = ''
                 rec.result = response.json()
                 temp =  response.json()
                 print("******************?",temp['data'])
            else:
                 print(f"Error:{response.status_code}")  
        
    
    def get_access(self,target='',pagination = False,pg_url=''):
        for rec in self:
            head = {"Accept":"application/json",
            'Authorization': 'token {}'.format('Bearer '+rec.token)}
            if target != '' and pagination == False :
                response = requests.request('GET',rec.url+target, headers=head)
            if target == '' and pagination == True :
                response = requests.request('GET',pg_url, headers=head)

            if response.status_code == 200:
                 rec.result = ''
                 rec.result = response.json()
                 temp =  response.json()
                 response.close()
                 return(temp)
            else:
                 print(f"Error:{response.status_code}")  

    def get_customer(self):
        for rec in self:
            partner = self.env['res.partner']
            ResCountryState = self.env['res.country.state']
            ResCountry = self.env['res.country']
            ResCurrency = self.env['res.currency']
            target = "customers"
            customers = rec.get_access(target)
            rec.result = customers
            partner_id = ''
            for p in range(customers['pagination']['totalPages']):
                u = ''
                # print("EEEEEEEEEEEEEEEEEEEeeeee",customers)
                if 'next' in customers['pagination']['links']:
                            u =customers['pagination']['links']['next']
                for d in customers['data']:
                    #  partner_id = ''
                     
                     if d['id']:
                        partner_id = partner.search(
                        [('salla_id', '=', d['id']), ('salla_integration_id', '=', self.id)], limit=1)
                     
                     if not partner_id and d['mobile']:
                        partner_id = partner.search(
                                [('mobile', '=', d['mobile']), ('salla_integration_id', '=', self.id)], limit=1)
                     if not partner_id and d['first_name'] != 'Заказ' and (d['first_name'] or d['last_name']):
                                partner_id = partner.search([('name', 'ilike', d['first_name'] + ' ' + d['last_name']),
                                             ('salla_integration_id', '=', self.id)], limit=1)
                     partner_country_id = ResCountry.search([('code', '=', d['country_code'])])
                     
                     if not partner_id:
                            partner_id = partner.create({
                                'name': d['first_name'] + ' ' + d['last_name'],
                                "company_type": 'person',
                                "mobile": d['mobile'],
                                "email": d['email'],
                                "salla_id":d['id'],
                                "salla_integration_id":rec.id,
                                # 'create_date': d['date_added'],
                                'child_ids': [[0, False, {
                                    'type': 'delivery',
                                    # 'name': order['shipping_firstname'] + ' ' + order['shipping_lastname'],
                                    # 'street': order['shipping_address_1'],
                                    # 'street2': order['shipping_address_2'],
                                    'city': d['city'],
                                    'state_id': ResCountryState.search([('code', '=', d['country_code']),
                                                                        ('country_id', '=', partner_country_id.id)]).id,
                                    # 'zip': order['shipping_postcode'],
                                    'country_id': partner_country_id.id,
                                    "email": d['email'],
                                    "mobile": d['mobile'],
                                    # 'create_date': d['updated_at']['date'],
                                }]]
                            })
                     print("EEEEEEEEEEEEEEEEEEEeeeee",partner_id)
                if u != '':                 
                        customers = rec.get_access(pagination=True,pg_url=u)
                else :
                                return True
            # return partner_id
   
   
    def get_categories(self):
        for rec in self:
              ProductCategory = self.env['product.category']
              target = 'categories'
              items = rec.get_access(target)
                # print('products')
              if items:
                for p in range(items['pagination']['totalPages']):
                  u = ''
                # print("EEEEEEEEEEEEEEEEEEEeeeee",customers)
                  if 'next' in items['pagination']['links']:
                            u = items['pagination']['links']['next']
                  for cate in items['data']:
                     product_category = ProductCategory.search([('salla_id', '=', cate['id'])])
                     if not  product_category:
                           ProductCategory.create(
                                {
                                     'parent_id':rec.parent_category_salla.id,
                                     'name':  cate['name'],
                                     'salla_id':cate['id']

                                })
                  if u != '':                 
                        items = rec.get_access(pagination=True,pg_url=u)
                  else :
                        return True

                
    def get_products(self):
        for rec in self:
             ProductTemplate = self.env['product.template']
             ProductProduct = self.env['product.product']
             ProductAttribute = self.env['product.attribute']
             ProductAttributeValue = self.env['product.attribute.value']
             ProductTemplateAttributeValue = self.env['product.template.attribute.value']
             ProductTemplateAttributeLine = self.env['product.template.attribute.line']
             ProductCategory = self.env['product.category']
             ProductPricelist = self.env['product.pricelist']
             ProductPricelistItem = self.env['product.pricelist.item']
             target = 'products'
            #  rec.result = products
             product_tmpl_id = ''
             product_category = ''
            #  for l in  items:
                # print("<<<<<<<<<<<<<<<<<<<<<<<<<@@@",l['id']) 
             items = rec.get_access(target)
                # print('products')
             for p in range(items['pagination']['totalPages']):
                u = ''
                if 'next' in items['pagination']['links']:
                            u =items['pagination']['links']['next']
                for product in items['data']:
                    product_tmpl_id = ProductTemplate.search(
                     [('salla_id', '=', product['id'])])
                    # dic = '' 
                    print('**********cate*****',product['categories'])
                    # if product['categories']:
                    #     for dic in product['categories']:
                    #         print('**********cate*****',dic)
                    #         product_category = ProductCategory.search([('salla_id', '=', dic['id'])])
                    #         if not product_category :
                    #             product_category = ProductCategory.create({
                    #                     'parent_id':rec.parent_category_salla.id,
                    #                     'name': dic['name'],
                    #                     'salla_id':dic['id']})
                    if not product_tmpl_id:
                        product_tmpl_id = ProductTemplate.create({
                            'name': product['name'],
                            'salla_id': product['id'],
                            'type': 'product',
                            # 'categ_id': product_category.id,
                        
                            # 'attribute_line_ids': attribute_line_ids
                        })

                    # category_id = ProductCategory.search([('name', '=', product['categories'])])
                    if product['categories']:
                        for dic in product['categories']:
                            print('**********cate*****',dic)
                            product_category = ProductCategory.search([('salla_id', '=', dic['id'])])
                            if not product_category :
                                product_category = ProductCategory.create({
                                        'parent_id':rec.parent_category_salla.id,
                                        'name': dic['name'],
                                        'salla_id':dic['id']})
                    
                        product_tmpl_id.categ_id = product_category.id

                    attribute_ids = []
                    value_ids = []

                    # choice next product
                    if not product['options']:
                       continue


                    for option in product['options']:
                       attribute_id = ProductAttribute.search([('salla_id', '=', option['id'])])
                       if not attribute_id:
                            attribute_id = ProductAttribute.create({'name': option['name'],
                                                              'salla_id':option['id']

                                })
                       for value in option['values']: 
                            

                            value_id = ProductAttributeValue.search(
                                              [('attribute_id', '=', attribute_id.id), ('name', '=', value['name'])], limit=1)
                            if not value_id:
                               value_id = ProductAttributeValue.create(
                                {'name': value['name'], 'attribute_id': attribute_id.id})
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
                if u != '':                 
                                    items = rec.get_access(pagination=True,pg_url=u)
                else :
                                    return True   




                   






    
    def get_order(self):
          for rec in self:
             SaleOrder = self.env['sale.order']
             SaleOrderLine = self.env['sale.order.line']
             ResCurrency = self.env['res.currency']
             CrmTeam = self.env['crm.team']
             ProductTemplate = self.env['product.template']
             ProductProduct = self.env['product.product']
             ProductAttribute = self.env['product.attribute']
             ProductAttributeValue = self.env['product.attribute.value']
             ProductTemplateAttributeValue = self.env['product.template.attribute.value']
             ProductTemplateAttributeLine = self.env['product.template.attribute.line']
             ProductCategory = self.env['product.category']
             ProductPricelist = self.env['product.pricelist']
             ProductPricelistItem = self.env['product.pricelist.item']
             AccountTax = self.env['account.tax']
             currency_id = self.env.company.currency_id
             target = "orders"
            #  print("LLLLLLLLLLLLLLLLLLLLLLLLLLLL")
             order_dict = rec.get_access(target)
            #  print('333################3',type(order_dict['pagination']['totalPages']))
            #  rec.get_customer()
            #  rec.result = orders
            #  for l in  orders:
            #  for p in range(order_dict['pagination']['totalPages']):
                    # u = ''
                    # if 'next' in order_dict['pagination']['links']:
                            # u =order_dict['pagination']['links']['next']
                    # print("$$$$$$$$$$$$$$$$$$$$$$",order_dict)  
             for orders in order_dict['data']:
                        # print('#################################>',orders)
                        saleorder_id = SaleOrder.search(
                                                [('salla_id', '=', orders['id']), ('salla_integration_id', '=', rec.id)], limit=1)
                        if not saleorder_id:
                            # print('************id****************>',orders['id'])

                            order = rec.get_access(target+ '/' + str(orders['id']))
                            # print('************item****************>',order['data']['items'])
                            # rec.get_products(order['data']['items'])
                        
                            
                            
                            # print('@@@ttttttttt@@@YYYYYYYYYYYYYYy@@@@@@@22',order['data']['items'])
                            partner_id = self.env['res.partner'].search([('salla_id','=',order['data']['customer']['id'])])
                            # print("????????????????????>>>>>>>>>",partner_id)
                            if not saleorder_id and  partner_id:
                                        saleorder_id = SaleOrder.create({
                                        'partner_id': partner_id.id,
                                        # 'date_order': ,
                                        "salla_id": order['data']['id'],
                                        "salla_integration_id": rec.id,
                                        "order_t":'salla',
                                        # 'team_id': CrmTeam.search([('name', '=', order['payment_country'])]).id,
                                        # 'pricelist_id': productpricelist_id.id,
                                        # 'create_date': order['date_added']
                                    })
                                        # print('@@@@@@@@@@@@@!!!!!!!!!!!!!!!>',saleorder_id)
                                        for p in order['data']['items']:
                                                # print(">>>>>>>>>>>>UUUUUUUUUU",p)
                                                # prod = rec.get_access(target='products'+'?product=' + str(p['id']))
                                                # print("<<<<<<<<<<<<<<<<<rrrrrr",prod)
                                                # for r in prod['data']['items']:
                                                #     p_id = r['id']
                                                product_id = self.env['product.product'].search([('name','=',p['name'])] ,limit=1)
                                                # print(">>>>>>>>>>>>UUUUUUUUUU*********?",p['name'])
                                                name='//'
                                                if product_id.name:
                                                    name = product_id.name
                                                SaleOrderLine.create({
                                                    'order_id': saleorder_id.id,
                                                    'name': name,
                                                    'product_id': product_id.id,
                                                    # 'product_uom': product_id.uom_id.id,
                                                    'product_uom_qty': p['quantity'],
                                                    # 'price_unit': price_unit,
                                                    # 'tax_id':  [(6, 0, tax_ids)],
                                                    })
                        # print("************>>>>>>>>>>>",order['pagination']['links'])
                    # if u != '':                 
                                    # order_dict = rec.get_access(pagination=True,pg_url=u)
                    # else :
                                    # return True
        # for rec in self:
        #      SaleOrder = self.env['sale.order']
        #      AccountMove = self.env['account.move']
        #      AccountMoveLine = self.env['account.move.line']
        #      SaleOrderLine = self.env['sale.order.line']
        #      ResCurrency = self.env['res.currency']
        #      CrmTeam = self.env['crm.team']
        #      ProductTemplate = self.env['product.template']
        #      ProductProduct = self.env['product.product']
        #      ProductAttribute = self.env['product.attribute']
        #      ProductAttributeValue = self.env['product.attribute.value']
        #      ProductTemplateAttributeValue = self.env['product.template.attribute.value']
        #      ProductTemplateAttributeLine = self.env['product.template.attribute.line']
        #      ProductCategory = self.env['product.category']
        #      ProductPricelist = self.env['product.pricelist']
        #      ProductPricelistItem = self.env['product.pricelist.item']
        #      AccountTax = self.env['account.tax']
        #      currency_id = self.env.company.currency_id
        #      target = "orders"
        #      print("LLLLLLLLLLLLLLLLLLLLLLLLLLLL")
        #      Orders = rec.get_access(target,u=False,pagination=False)
        #      if Orders:
                
        #         rec.get_customer()
        #         print("########################################>>",Orders)
        #         #  rec.result = orders
        #     #    for l in  orders:
                
        #         while Orders['data']:
        #                 for orders in Orders['data']:
                                
        #                         order = rec.get_access(target+ '/' + str(orders['id']),u=False,pagination=False)
        #                         print("(((((((((((((((((((((",order)
        #                         rec.get_products(order['data']['items'])
        #                         # for o in order['data']:
        #                         # print("@@@@@@@@@@@@@@@@@22",order)
        #                         account_move_id = AccountMove.search(
        #                                                 [('salla_id', '=', order['data']['id']), ('salla_integration_id', '=', rec.id)], limit=1)
                                
        #                         print('@@@@@@@@@@@@@22',account_move_id)
        #                         partner_id = self.env['res.partner'].search([('salla_id','=',order['data']['customer']['id'])])
        #                         print("????????????????????>>>>>>>>>",partner_id)
        #                         if not account_move_id and  partner_id:
        #                                 account_move_id = AccountMove.create({
        #                                     'partner_id': partner_id.id,
        #                                     # 'date_order': ,
        #                                     "salla_id": order['data']['id'],
        #                                     "salla_integration_id": rec.id,
        #                                     "move_type":"out_invoice",
        #                                     "state":"draft",

        #                                     # 'team_id': CrmTeam.search([('name', '=', order['payment_country'])]).id,
        #                                     # 'pricelist_id': productpricelist_id.id,
        #                                 #   'create_date': Date.today()
        #                                 })
        #                                 product_shipping_id = self.env['product.product'].search([('salla_id','=',order['data']['shipping']['id'])])
        #                                 if not product_shipping_id:
        #                                     product_shipping_id = ProductTemplate.create({
        #                                             'name': "Delivery" + order['data']['shipping']['company'],
        #                                             'salla_id': order['data']['shipping']['id'],
        #                                             'type': 'product',
        #                                             'list_price': order['data']['amounts']['shipping_cost']['amount']
                                                    
        #                                         })

        #                                 print('@@@@@@@@@@@@@##########################',order['data']['amounts']['shipping_cost']['amount'])
                                        
        #                                 if partner_id:
        #                                     product_shipping_id = self.env['product.product'].search([('salla_id','=',order['data']['shipping']['id'])])
        #                                     print('@@@@@@@@@@@@@!!!!!!!!!!!!!!!>',product_shipping_id.name)
        #                                     if product_shipping_id:
        #                                         AccountMoveLine.with_context(check_move_validity=False).create({
        #                                                 'move_id': account_move_id.id,
        #                                                 'name': product_shipping_id.name,
        #                                                 'product_id': product_shipping_id.id,
        #                                                 # 'product_uom': product_id.uom_id.id,
        #                                                 'quantity': 1,
        #                                                 "account_id":158,
        #                                                 "price_unit":product_shipping_id.list_price,
        #                                                 # "credit":product_shipping_id.list_price
        #                                                 # "check_move_validity":False

        #                                                 # 'price_unit': price_unit,
        #                                                 # 'tax_id':  [(6, 0, tax_ids)],
        #                                                     })
        #                                     for p in order['data']['items']:
        #                                         # print(">>>>>>>>>>>>UUUUUUUUUU",p)
        #                                         product_id = self.env['product.product'].search([('salla_id','=',p['id'])])
        #                                         print(">>>>>>>>>>>>UUUUUUUUUU",product_id)
        #                                         AccountMoveLine.with_context(check_move_validity=False).create({
        #                                             'move_id': account_move_id.id,
        #                                             'name': product_id.name,
        #                                             'product_id': product_id.id,
        #                                             # 'product_uom': product_id.uom_id.id,
        #                                             'quantity': p['quantity'],
        #                                             "account_id":158,
        #                                             "price_unit":product_id.list_price,
        #                                             "credit":product_id.list_price
        #                                             # "check_move_validity":False

        #                                             # 'price_unit': price_unit,
        #                                             # 'tax_id':  [(6, 0, tax_ids)],
        #                                                  })
        #                 print('*********************@@@>',Orders['pagination']['links'])
        #                 if 'next' in Orders['pagination']['links']:
        #                     Orders = rec.get_access(target,u=Orders['pagination']['links']['next'],pagination=True)
        #                 else :
        #                     return
                



    
                            
            
