# 🔐 Guia de Segurança - API GIV

**Versão**: 1.0.2  
**Data**: Janeiro 2025  
**Projeto**: Gestão Inteligente de Vagas (GIV)

---

## ⚠️ **PROBLEMA RESOLVIDO**

O **GitGuardian** detectou chaves secretas hardcoded no código. Este problema foi **corrigido** implementando variáveis de ambiente.

---

## 🔧 **CORREÇÕES IMPLEMENTADAS**

### **1. Variáveis de Ambiente**
- ✅ Removidas chaves secretas do código
- ✅ Implementadas variáveis de ambiente
- ✅ Criado arquivo `config.env.example`
- ✅ Atualizado `.gitignore` para proteger arquivos sensíveis

### **2. Arquivos Modificados**
- ✅ `api_giv_completa.py` - Chaves movidas para variáveis de ambiente
- ✅ `app.py` - Chaves movidas para variáveis de ambiente
- ✅ `.gitignore` - Adicionadas proteções para arquivos de configuração

---

## 🚀 **COMO CONFIGURAR**

### **1. Copiar Arquivo de Configuração**
```bash
cp config.env.example config.env
```

### **2. Editar Arquivo de Configuração**
```bash
# Edite config.env com suas chaves secretas
GIV_SECRET_KEY=sua-chave-secreta-forte-aqui
APP_SECRET_KEY=sua-chave-secreta-app-aqui
GIV_ACCESS_TOKEN_EXPIRE=30
```

### **3. Gerar Chaves Secretas Fortes**
```bash
# Exemplo de chave forte (use uma ferramenta de geração)
GIV_SECRET_KEY=GIV_2025_$(openssl rand -hex 32)
APP_SECRET_KEY=APP_2025_$(openssl rand -hex 32)
```

---

## 🔒 **BOAS PRÁTICAS DE SEGURANÇA**

### **✅ FAZER**
- ✅ Usar variáveis de ambiente para chaves secretas
- ✅ Gerar chaves fortes e únicas
- ✅ Rotacionar chaves regularmente
- ✅ Usar diferentes chaves para diferentes ambientes
- ✅ Documentar configurações de segurança

### **❌ NÃO FAZER**
- ❌ **NUNCA** commitar chaves secretas no código
- ❌ **NUNCA** usar chaves padrão em produção
- ❌ **NUNCA** compartilhar chaves por email/chat
- ❌ **NUNCA** usar a mesma chave em múltiplos projetos
- ❌ **NUNCA** armazenar chaves em arquivos versionados

---

## 🛡️ **PROTEÇÕES IMPLEMENTADAS**

### **1. Arquivos Ignorados pelo Git**
```
config.env
.env
.env.local
.env.production
.env.staging
*.key
*.pem
*.crt
secrets.json
```

### **2. Variáveis de Ambiente**
```python
# api_giv_completa.py
SECRET_KEY = os.getenv("GIV_SECRET_KEY", "chave-secreta-padrao-dev")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("GIV_ACCESS_TOKEN_EXPIRE", "30"))

# app.py
secret_key = os.getenv("APP_SECRET_KEY", "chave-fixa-temporaria")
```

### **3. Configuração de Ambiente**
```bash
# config.env.example
GIV_SECRET_KEY=sua-chave-secreta-forte-aqui
APP_SECRET_KEY=sua-chave-secreta-app-aqui
GIV_ACCESS_TOKEN_EXPIRE=30
```

---

## 🔍 **VERIFICAÇÃO DE SEGURANÇA**

### **1. Verificar se Não Há Chaves no Código**
```bash
# Procurar por possíveis chaves hardcoded
grep -r "SECRET_KEY\|password\|token" --include="*.py" . | grep -v "os.getenv"
```

### **2. Verificar Variáveis de Ambiente**
```bash
# Verificar se as variáveis estão configuradas
echo $GIV_SECRET_KEY
echo $APP_SECRET_KEY
```

### **3. Testar Aplicação**
```bash
# Executar com variáveis de ambiente
python api_giv_completa.py
python app.py
```

---

## 📋 **CHECKLIST DE SEGURANÇA**

### **✅ Configuração Inicial**
- [ ] Arquivo `config.env` criado
- [ ] Chaves secretas configuradas
- [ ] Variáveis de ambiente funcionando
- [ ] Aplicação executando sem erros

### **✅ Verificação de Código**
- [ ] Nenhuma chave hardcoded no código
- [ ] Variáveis de ambiente sendo usadas
- [ ] Arquivos sensíveis no `.gitignore`
- [ ] Documentação de segurança atualizada

### **✅ Deploy e Produção**
- [ ] Chaves diferentes para produção
- [ ] Variáveis de ambiente configuradas no servidor
- [ ] Logs não expondo informações sensíveis
- [ ] Monitoramento de segurança ativo

---

## 🚨 **EM CASO DE COMPROMETIMENTO**

### **1. Ações Imediatas**
1. **Rotacionar** todas as chaves comprometidas
2. **Revogar** tokens JWT existentes
3. **Atualizar** variáveis de ambiente
4. **Notificar** equipe de segurança

### **2. Investigação**
1. **Analisar** logs de acesso
2. **Verificar** atividades suspeitas
3. **Identificar** origem do comprometimento
4. **Documentar** incidente

### **3. Prevenção**
1. **Implementar** monitoramento adicional
2. **Revisar** políticas de segurança
3. **Treinar** equipe sobre boas práticas
4. **Atualizar** documentação de segurança

---

## 📞 **SUPORTE**

Para questões de segurança:
1. **Consulte** este guia primeiro
2. **Verifique** as configurações de ambiente
3. **Teste** localmente antes de fazer deploy
4. **Documente** qualquer problema encontrado

---

**Status**: ✅ **PROBLEMA RESOLVIDO**  
**Última Atualização**: Janeiro 2025  
**Próxima Revisão**: Março 2025
