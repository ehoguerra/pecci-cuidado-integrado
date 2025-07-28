# Sistema de Footer Unificado

## Visão Geral

O sistema de footer foi centralizado para facilitar a manutenção e garantir consistência visual em todas as páginas do site.

## Estrutura

### Arquivos do Sistema

1. **`templates/includes/footer.html`** - Template base do footer
2. **`static/css/footer.css`** - Estilos CSS específicos do footer
3. **Este arquivo de documentação** - Guia de uso

### Arquivos que Utilizam o Sistema

- `templates/index.html` (página principal)
- `templates/login.html` (página de login)
- `templates/register.html` (página de registro)
- `templates/blog.html` (página do blog)
- `templates/view_blog_post.html` (visualização de posts do blog)

## Como Usar

### 1. Incluindo o Footer em uma Nova Página

Para adicionar o footer unificado em uma nova página:

1. **Inclua o CSS do footer no `<head>`:**
```html
<!-- Footer CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/footer.css') }}">
```

2. **Inclua o template do footer antes do fechamento do `<body>`:**
```html
{% include 'includes/footer.html' %}
```

### 2. Exemplo Completo

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minha Página - Pecci Cuidado Integrado</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <!-- Footer CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/footer.css') }}">
</head>
<body>
    <!-- Conteúdo da página aqui -->
    
    {% include 'includes/footer.html' %}
    
    <!-- Scripts antes do fechamento do body -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

## Personalização

### Modificando Informações do Footer

Para alterar informações como endereço, telefone, horários de funcionamento, etc., edite o arquivo:
**`templates/includes/footer.html`**

### Modificando Estilos do Footer

Para alterar cores, fontes, espaçamentos, etc., edite o arquivo:
**`static/css/footer.css`**

## Vantagens do Sistema

1. **Centralização**: Todas as alterações são feitas em um único local
2. **Consistência**: Garantia de que todas as páginas terão o mesmo footer
3. **Manutenibilidade**: Fácil de atualizar informações e estilos
4. **Reutilização**: Pode ser facilmente incluído em novas páginas
5. **Performance**: CSS separado permite melhor cache e organização

## Informações Atuais do Footer

### Seção 1: Empresa
- Nome: Pecci Cuidado Integrado
- Descrição
- Redes sociais (Facebook, Instagram, WhatsApp, LinkedIn)

### Seção 2: Contato
- Endereço: Rua das Flores, 123 - Centro, São Paulo, SP - CEP 01234-567
- Telefone: (11) 9999-9999
- Email: contato@peccicuidado.com.br

### Seção 3: Horário de Funcionamento
- Segunda a Sexta: 08:00 às 18:00
- Sábado: 08:00 às 12:00
- Domingo: Fechado

### Rodapé
- Copyright 2025 Pecci Cuidado Integrado
- Link para "Área do Psicólogo"

## Responsividade

O footer é totalmente responsivo e se adapta a diferentes tamanhos de tela:
- Desktop: Layout de 3 colunas
- Tablet: Layout adaptativo
- Mobile: Layout de coluna única centralizada

## Dependências

- Bootstrap 5.3.0
- Font Awesome 6.0.0
- Google Fonts (Poppins)

## Manutenção

Para manter o sistema sempre atualizado:

1. **Verificar links** - Testar periodicamente se todos os links funcionam
2. **Atualizar informações** - Manter contatos e horários sempre atualizados
3. **Testar responsividade** - Verificar em diferentes dispositivos
4. **Backup** - Manter backup dos arquivos do sistema

## Troubleshooting

### Problemas Comuns

1. **Footer não aparece**: Verificar se o include está correto
2. **Estilos não funcionam**: Verificar se o CSS foi incluído no head
3. **Layout quebrado**: Verificar se o Bootstrap está carregado
4. **Ícones não aparecem**: Verificar se o Font Awesome está carregado

### Suporte

Para dúvidas ou problemas com o sistema de footer, consulte este documento ou verifique os arquivos de exemplo nas páginas existentes.
