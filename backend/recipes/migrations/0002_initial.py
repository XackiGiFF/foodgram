# Generated by Django 4.2.5 on 2023-10-29 21:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.AmountIngredient', to='recipes.ingredient', verbose_name='Ингредиенты блюда'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.tag', verbose_name='Тег'),
        ),
        migrations.AddField(
            model_name='ordercart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart', to='recipes.recipe', verbose_name='Список покупок'),
        ),
        migrations.AddField(
            model_name='ordercart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_for_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.CheckConstraint(check=models.Q(('name__length__gt', 0)), name='\nrecipes_ingredient_name is empty\n'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.CheckConstraint(check=models.Q(('measurement_unit__length__gt', 0)), name='\nrecipes_ingredient_measurement_unit is empty\n'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='recipes.recipe', verbose_name='Список избранных рецептов'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Владелец списка избранного'),
        ),
        migrations.AddField(
            model_name='amountingredient',
            name='ingredients',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amount_ingredients', to='recipes.ingredient', verbose_name='Связанные ингредиенты'),
        ),
        migrations.AddField(
            model_name='amountingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amount_ingredients', to='recipes.recipe', verbose_name='В каких рецептах'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('name', 'author'), name='unique_for_author'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.CheckConstraint(check=models.Q(('name__length__gt', 0)), name='\nrecipes_recipe_name is empty\n'),
        ),
        migrations.AddConstraint(
            model_name='ordercart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='recipes_shoppingcart_unique'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='recipes_favorites_unique'),
        ),
        migrations.AddConstraint(
            model_name='amountingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredients'), name='\nrecipes_amountingredient ingredient alredy added\n'),
        ),
    ]
