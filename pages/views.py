from django.views.generic import TemplateView


class TopView(TemplateView):
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['pages/top.html']
        return ['pages/landing.html']
