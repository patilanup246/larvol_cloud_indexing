from django.shortcuts import render
from django.views.generic import TemplateView
import xlwt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from strgen import StringGenerator as SG
from pymongo import MongoClient,  DESCENDING
from django.utils.http import is_safe_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.contrib.auth.decorators import login_required, permission_required

client = MongoClient()
db = client.LARVOL_CLOUD
crawl_initiate = db.CRAWLING_INITIATES
crawled_data = db.CRAWLED_DATA



class loginView(FormView):
    success_url = '/homepage'
    template_name = "login.html"
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(loginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(loginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.success_url
        return redirect_to


class homepageView(TemplateView):
    template_name =  "homepage.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(self.__class__, self).dispatch(request, *args, **kwargs)

    def get_data(self):
        data_to = []
        for data in crawl_initiate.find({}).sort('_id',DESCENDING):
            data_dict = {
                "idd": str(data['_id']),
                "crawl_id": data['crawl_id'],
                "conf":data['conf'],
                "start_datetime": data['start_datetime'],
                "end_datetime":data['end_datetime'],
                "status":data['status'],
            }
            data_to.append(data_dict)

        return data_to


    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['recent_data'] = self.get_data()
        return context


class view_dataView(TemplateView):
    template_name = "view.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(self.__class__, self).dispatch(request, *args, **kwargs)

    def get_all_rows(self, crawl_id):
        all_data = []
        for data in crawled_data.find({'crawl_id':crawl_id}):
            data_dict = {
                "source_id": data['source_id'],
                "session_id": data['session_id'],
                "crawl_id": data['crawl_id'],
                "session_title": data['session_title'],
                "article_title": data['article_title'],
                "start_time": data['start_time'],
                "end_time": data['end_time'],
                "date": data['date'],
                "session_type": data['session_type'],
                "chairs": data['chairs'],
                "authors": data['authors'],
                "authors_affiliations": data['authors_affiliations'],
                "chairs_affiliations": data['chairs_affiliations'],
                "location": data['location'],
                "url": data['url'],
            }
            all_data.append(data_dict)
        return all_data, len(all_data)



    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        data_id = kwargs['string']
        all_response,count = self.get_all_rows(data_id)
        context['all_data'] = all_response
        context['total_rows'] = count
        context['data_id'] = data_id
        return context

class LogoutView(RedirectView):
    url = '/'
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

login = loginView.as_view()
homepage = homepageView.as_view()
view_data = view_dataView.as_view()
logout = LogoutView.as_view()


# EXPORT DATA

def getData(crawl_id):
    return crawl_initiate.find_one({'crawl_id':crawl_id})

def getDataExported(crawl_id):
    all_data = []
    for data in crawled_data.find({'crawl_id':crawl_id}):
        my_data = []
        my_data.append(data['source_id'])
        my_data.append(data['session_id'])
        my_data.append(data['article_title'])
        my_data.append(data['url'])
        my_data.append(data['authors'])
        my_data.append(data['authors_affiliations'])
        my_data.append(data['chairs'])
        my_data.append(data['chairs_affiliations'])
        my_data.append(data['date'])
        my_data.append(data['start_time'])
        my_data.append(data['end_time'])
        my_data.append(' ')
        my_data.append(data['location'])
        my_data.append(data['session_title'])
        my_data.append(data['session_type'])
        all_data.append(tuple(my_data))
    return all_data


def export_data(request, string):
    instance = getData(string)
    rows = getDataExported(string)
    response = HttpResponse(content_type='application/ms-excel')
    text_data = SG("[\l\d]{10}").render()
    file_name = "{0}_{1}.xls".format(instance['conf'], text_data)
    content_dispotion = 'attachment; filename="{0}"'.format(file_name)
    response['Content-Disposition'] = content_dispotion

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(instance['conf'])
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['source_id','session_id', 'article_title','url',
               'authors', 'authors_affiliations', 'chairs', 'chairs_affiliations',
               'date', 'start_time', 'end_time','abstract_text', 'location',
               'session_title', 'session_type', 'category', 'disclosure',]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response