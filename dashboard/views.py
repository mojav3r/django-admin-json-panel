import json

from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView

from dashboard.forms import UserLoginForm, JsonUploadForm
from dashboard.utils import get_search_results, handle_merge
from json_handler.models import JSONData
from laboratory_django import settings


class UserLoginView(View):
    template_name = 'dashboard/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('dashboard:dashboard'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        login_form = UserLoginForm()
        context = {
            'form': login_form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        login_form = UserLoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user: User = User.objects.filter(username__exact=username).first()
            if user is not None:
                if not user.is_active:
                    login_form.add_error('password', 'This account is not active')
                else:
                    is_password_correct = user.check_password(password)
                    if is_password_correct:
                        login(request, user)
                        return redirect(reverse('dashboard:dashboard'))
                    else:
                        login_form.add_error('password', 'Username or Password incorrect')
            else:
                login_form.add_error('password', 'Username or Password incorrect')

        context = {
            'form': login_form,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect(reverse('dashboard:user_login'))


@method_decorator(login_required, name='dispatch')
class DashboardView(ListView):
    template_name = 'dashboard/index.html'
    model = JSONData
    context_object_name = 'datas'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = JSONData.objects.count()
        search_term = self.request.GET.get('q', '')
        context['q'] = search_term
        context['search_count'] = self.get_queryset().count()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('q', '')
        if search_term:
            queryset = get_search_results(queryset, search_term)
        return queryset

    def post(self, request, *args, **kwargs):
        if 'action' in request.POST:
            action = request.POST.get('action_selector')
            ids = request.POST.get('ids')
            if ids != '':
                if action == 'delete_selected':
                    ids_list = json.loads(ids)
                    count = len(ids_list)
                    JSONData.objects.filter(id__in=ids_list).delete()
                    messages.success(request, f"Successfully deleted {count} json data")
                    return redirect('dashboard:dashboard')
                    # messages.warning(request, "Your account expires in three days.")
                    # messages.error(request, "Document deleted.")
                elif action == 'merge_selected':
                    ids_list = json.loads(ids)
                    file_name = handle_merge(ids_list)
                    return redirect('json:download', name=file_name)
                else:
                    messages.error(request, f"No action selected.")
                    return redirect('dashboard:dashboard')
            else:
                messages.error(request,
                               f"Items must be selected in order to perform actions on them. No items have been changed")
                return redirect('dashboard:dashboard')

        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class DataDetailView(DetailView):
    template_name = 'dashboard/detail.html'
    model = JSONData
    context_object_name = 'data'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(JSONData, pk=pk)
        return obj


@method_decorator(login_required, name='dispatch')
class AddDataView(View):
    template_name = 'dashboard/add.html'
    form_class = JsonUploadForm

    def get(self, request):
        context = {
            'form': self.form_class(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            author = request.POST.get('author')
            new_json_file = request.FILES['upload']
            try:
                new_data = json.loads(new_json_file.read().decode('utf-8'))

                for key, value in new_data.items():
                    exists = False
                    for obj in JSONData.objects.all():
                        if key in obj.data and obj.data[key] == value:
                            exists = True
                            break

                    if not exists:
                        JSONData.objects.create(upload=new_json_file, data={key: value}, author=author)

                messages.success(request, 'JSON data uploaded successfully.')
                return redirect('dashboard:add_data')

            except json.JSONDecodeError:
                messages.error(request, 'Uploaded file is not a valid JSON.')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

        context = {
            'form': form,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class DownloadData(View):
    def get(self, request, pk):
        try:
            obj = JSONData.objects.get(pk=pk)
            data = obj.data
            json_data = json.dumps(data, indent=4)

            temp_file_path = settings.MEDIA_ROOT + 'files'
            with open(temp_file_path, 'w') as f:
                f.write(json_data)

            with open(temp_file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/json')
                response['Content-Disposition'] = f'attachment; filename="{obj.pk}.json"'
            return response

        except JSONData.DoesNotExist:
            return JsonResponse({"data": "File does not exist"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
