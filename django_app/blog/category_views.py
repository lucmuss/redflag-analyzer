"""
Blog Category Management Views (Staff Only)
"""
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from .admin_views import StaffRequiredMixin
from .models import BlogCategory


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = BlogCategory
    template_name = 'blog/admin/category_form.html'
    fields = ['name', 'slug', 'icon', 'description', 'category_type', 'is_active', 'meta_description']
    success_url = reverse_lazy('blog:admin_categories')
    
    def form_valid(self, form):
        messages.success(self.request, f'✓ Kategorie "{form.instance.name}" wurde erstellt.')
        return super().form_valid(form)


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = BlogCategory
    template_name = 'blog/admin/category_form.html'
    fields = ['name', 'slug', 'icon', 'description', 'category_type', 'is_active', 'meta_description']
    success_url = reverse_lazy('blog:admin_categories')
    
    def form_valid(self, form):
        messages.success(self.request, f'✓ Kategorie "{form.instance.name}" wurde aktualisiert.')
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = BlogCategory
    template_name = 'blog/admin/category_confirm_delete.html'
    success_url = reverse_lazy('blog:admin_categories')
    
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, f'✓ Kategorie "{category.name}" wurde gelöscht.')
        return super().delete(request, *args, **kwargs)
