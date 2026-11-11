from django.contrib import admin


def unfold(request):
    """Mesmo contexto do admin (cores, tema, títulos) para as telas do site usarem o layout do Unfold."""
    if request.path.startswith("/admin/"):
        return {}  # o admin já monta o próprio contexto
    return admin.site.each_context(request)
