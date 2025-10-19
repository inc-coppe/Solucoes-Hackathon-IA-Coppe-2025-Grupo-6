"""
Módulo de Machine Learning para Predição de Agravamentos em Saúde
==================================================================

Este módulo implementa um modelo de ML que prediz a probabilidade de 
agravamento de pacientes sem agendamento, baseado em dados históricos.

Algoritmo: Random Forest Classifier
Features: Risco, Especialidade, Faixa Etária, Tempo de Espera, Status
"""

import polars as pl
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class ModeloPredicaoAgravamento:
    """
    Modelo de Machine Learning para predição de agravamentos
    """
    
    def __init__(self):
        self.modelo = None
        self.encoders = {}
        self.feature_importance = None
        self.metricas = {}
        self.treinado = False
        
    def preparar_features(self, df):
        """
        Feature Engineering: Extração e transformação de características
        
        Features utilizadas:
        1. solicitacao_risco (categórica) → Nível de risco do paciente
        2. procedimento_especialidade (categórica) → Especialidade médica
        3. paciente_faixa_etaria (categórica) → Faixa etária
        4. tempo_espera_dias (numérica) → Dias aguardando atendimento
        5. status_critico (binária) → Se status indica situação crítica
        """
        
        # Criar cópia para não modificar original
        df_features = df.clone()
        
        # Feature 1: Risco (já categórica, vamos codificar)
        if 'solicitacao_risco' in df_features.columns:
            # Primeiro, tratar valores nulos e desconhecidos
            df_features = df_features.with_columns(
                pl.col('solicitacao_risco').fill_null("DESCONHECIDO")
            )
            
            risco_map = {'VERMELHO': 4, 'AMARELO': 3, 'VERDE': 2, 'AZUL': 1, 'DESCONHECIDO': 0}
            df_features = df_features.with_columns(
                pl.col('solicitacao_risco').replace(risco_map, default=0).alias('risco_numerico')
            )
        
        # Feature 2: Tempo de espera (simulado se não existir)
        # Em produção, seria calculado: data_atual - data_solicitacao
        if 'data_solicitacao' not in df_features.columns:
            # Simulação baseada no risco (mais crítico = mais urgente)
            np.random.seed(42)
            df_features = df_features.with_columns(
                pl.lit(np.random.randint(1, 120, len(df_features))).alias('tempo_espera_dias')
            )
        
        # Feature 3: Faixa Etária (codificar categorias)
        if 'paciente_faixa_etaria' in df_features.columns:
            # Extrair idade média da faixa
            df_features = df_features.with_columns(
                pl.col('paciente_faixa_etaria').str.extract(r'(\d+)', 1)
                .cast(pl.Int32, strict=False)
                .fill_null(40)
                .alias('idade_aproximada')
            )
        else:
            df_features = df_features.with_columns(pl.lit(40).alias('idade_aproximada'))
        
        # Feature 4: Especialidade (label encoding)
        if 'procedimento_especialidade' in df_features.columns:
            # Primeiro, substituir nulos por "DESCONHECIDA"
            df_features = df_features.with_columns(
                pl.col('procedimento_especialidade').fill_null("DESCONHECIDA")
            )
            
            # Agora obter todas as especialidades únicas (incluindo "DESCONHECIDA")
            especialidades_unicas = df_features['procedimento_especialidade'].unique().to_list()
            
            # Criar mapeamento incluindo "DESCONHECIDA"
            esp_map = {esp: idx for idx, esp in enumerate(especialidades_unicas)}
            
            df_features = df_features.with_columns(
                pl.col('procedimento_especialidade')
                .replace(esp_map)
                .alias('especialidade_codigo')
            )
            
            self.encoders['especialidade'] = esp_map
        
        # Feature 5: Status crítico (se contém palavras-chave)
        if 'solicitacao_status' in df_features.columns:
            df_features = df_features.with_columns(
                pl.col('solicitacao_status')
                .str.contains('CRITICO|URGENTE|GRAVE')
                .fill_null(False)
                .cast(pl.Int32)
                .alias('status_critico')
            )
        else:
            df_features = df_features.with_columns(pl.lit(0).alias('status_critico'))
        
        return df_features
    
    def criar_target(self, df):
        """
        Criar variável target (agravamento) baseada em regras de negócio
        
        Consideramos que um paciente teve agravamento se:
        - Risco VERMELHO e tempo > 30 dias
        - Risco AMARELO e tempo > 60 dias
        - Status contém palavras críticas
        
        Em produção, isso viria de dados históricos reais de outcomes
        """
        df_target = df.clone()
        
        # Simulação de agravamento baseada em regras + aleatoriedade
        np.random.seed(42)
        
        # Probabilidades base por risco
        prob_agravamento = []
        for i in range(len(df_target)):
            row = df_target.row(i, named=True)
            
            risco = row.get('solicitacao_risco', 'AZUL')
            tempo = row.get('tempo_espera_dias', 0)
            
            # Probabilidade base
            if risco == 'VERMELHO':
                prob = 0.7 + (tempo / 100) * 0.2
            elif risco == 'AMARELO':
                prob = 0.4 + (tempo / 150) * 0.2
            elif risco == 'VERDE':
                prob = 0.15 + (tempo / 200) * 0.1
            elif risco == 'AZUL':
                prob = 0.05 + (tempo / 250) * 0.05
            else:  # DESCONHECIDO ou outros
                prob = 0.1 + (tempo / 300) * 0.05
            
            # Adiciona aleatoriedade
            prob = min(prob + np.random.normal(0, 0.1), 1.0)
            prob = max(prob, 0.0)
            
            agravou = 1 if np.random.random() < prob else 0
            prob_agravamento.append(agravou)
        
        df_target = df_target.with_columns(
            pl.Series('agravamento', prob_agravamento)
        )
        
        return df_target
    
    def treinar(self, df):
        """
        Treina o modelo de Machine Learning
        
        Processo:
        1. Feature Engineering
        2. Criação do target
        3. Split treino/teste (80/20)
        4. Treinamento do Random Forest
        5. Avaliação de métricas
        """
        
        print("🤖 INICIANDO TREINAMENTO DO MODELO DE ML")
        print("=" * 60)
        
        # 1. Preparar features
        print("📊 Passo 1: Feature Engineering...")
        df_prep = self.preparar_features(df)
        df_prep = self.criar_target(df_prep)
        
        # Selecionar colunas de features
        feature_cols = ['risco_numerico', 'tempo_espera_dias', 'idade_aproximada', 
                       'especialidade_codigo', 'status_critico']
        
        # Verificar se todas as features existem
        feature_cols_existentes = [col for col in feature_cols if col in df_prep.columns]
        
        # Converter para numpy arrays
        X = df_prep.select(feature_cols_existentes).to_numpy()
        y = df_prep['agravamento'].to_numpy()
        
        print(f"   ✅ Features extraídas: {len(feature_cols_existentes)}")
        print(f"   ✅ Amostras: {len(X):,}")
        print(f"   ✅ Taxa de agravamento: {y.mean():.1%}")
        
        # 2. Split treino/teste
        print("\n📊 Passo 2: Divisão Treino/Teste (80/20)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"   ✅ Treino: {len(X_train):,} amostras")
        print(f"   ✅ Teste: {len(X_test):,} amostras")
        
        # 3. Treinamento do modelo
        print("\n🌲 Passo 3: Treinando Random Forest Classifier...")
        self.modelo = RandomForestClassifier(
            n_estimators=100,        # 100 árvores de decisão
            max_depth=10,            # Profundidade máxima
            min_samples_split=20,    # Mínimo de amostras para split
            min_samples_leaf=10,     # Mínimo de amostras por folha
            random_state=42,
            n_jobs=-1                # Usar todos os cores
        )
        
        self.modelo.fit(X_train, y_train)
        print("   ✅ Modelo treinado com sucesso!")
        
        # 4. Avaliação
        print("\n📈 Passo 4: Avaliação do Modelo...")
        y_pred = self.modelo.predict(X_test)
        y_pred_proba = self.modelo.predict_proba(X_test)[:, 1]
        
        # Métricas
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        acuracia = accuracy_score(y_test, y_pred)
        precisao = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        try:
            auc_roc = roc_auc_score(y_test, y_pred_proba)
        except:
            auc_roc = 0.0
        
        self.metricas = {
            'acuracia': acuracia,
            'precisao': precisao,
            'recall': recall,
            'f1_score': f1,
            'auc_roc': auc_roc,
            'total_treino': len(X_train),
            'total_teste': len(X_test)
        }
        
        print(f"   ✅ Acurácia: {acuracia:.1%}")
        print(f"   ✅ Precisão: {precisao:.1%}")
        print(f"   ✅ Recall: {recall:.1%}")
        print(f"   ✅ F1-Score: {f1:.1%}")
        print(f"   ✅ AUC-ROC: {auc_roc:.3f}")
        
        # 5. Feature Importance
        self.feature_importance = {
            'features': feature_cols_existentes,
            'importances': self.modelo.feature_importances_.tolist()
        }
        
        print("\n🎯 Importância das Features:")
        for feat, imp in zip(feature_cols_existentes, self.modelo.feature_importances_):
            print(f"   {feat}: {imp:.3f}")
        
        self.treinado = True
        print("\n" + "=" * 60)
        print("✅ MODELO TREINADO COM SUCESSO!")
        print("=" * 60)
        
        return self.metricas
    
    def predizer_agravamentos(self, df_sem_agendamento):
        """
        Prediz probabilidade de agravamento para pacientes sem agendamento
        
        Retorna DataFrame com colunas adicionais:
        - probabilidade_agravamento
        - risco_ml (classificação ML)
        """
        
        if not self.treinado:
            print("⚠️ Modelo não treinado! Treinando agora...")
            # Se não foi treinado, usa os próprios dados para treinar
            # (em produção, usaria dados históricos separados)
            self.treinar(df_sem_agendamento)
        
        # Preparar features
        df_pred = self.preparar_features(df_sem_agendamento)
        
        feature_cols = ['risco_numerico', 'tempo_espera_dias', 'idade_aproximada', 
                       'especialidade_codigo', 'status_critico']
        feature_cols_existentes = [col for col in feature_cols if col in df_pred.columns]
        
        X = df_pred.select(feature_cols_existentes).to_numpy()
        
        # Predições
        probabilidades = self.modelo.predict_proba(X)[:, 1]
        predicoes = self.modelo.predict(X)
        
        # Adicionar ao DataFrame
        df_pred = df_pred.with_columns([
            pl.Series('probabilidade_agravamento', probabilidades),
            pl.Series('predicao_agravamento', predicoes)
        ])
        
        return df_pred
    
    def calcular_metricas_predicao(self, df_predicoes):
        """
        Calcula métricas de predição para o dashboard
        """
        
        total = len(df_predicoes)
        
        # Agravamentos por faixa de probabilidade
        alto_risco = df_predicoes.filter(pl.col('probabilidade_agravamento') > 0.7).height
        medio_risco = df_predicoes.filter(
            (pl.col('probabilidade_agravamento') > 0.4) & 
            (pl.col('probabilidade_agravamento') <= 0.7)
        ).height
        baixo_risco = df_predicoes.filter(pl.col('probabilidade_agravamento') <= 0.4).height
        
        # Projeções
        agravamentos_30_dias = int(alto_risco * 0.9)  # 90% dos alto risco
        agravamentos_60_dias = int(medio_risco * 0.5)  # 50% dos médio risco
        agravamentos_90_dias = int(baixo_risco * 0.1)  # 10% dos baixo risco
        
        # Custos
        custo_unitario = 5000
        custo_30_dias = agravamentos_30_dias * custo_unitario
        custo_total = (agravamentos_30_dias + agravamentos_60_dias + agravamentos_90_dias) * custo_unitario
        
        # Internações
        internacoes = int((agravamentos_30_dias + agravamentos_60_dias + agravamentos_90_dias) * 0.30)
        
        # Top especialidades por risco ML
        df_esp = df_predicoes.group_by('procedimento_especialidade').agg([
            pl.count().alias('total'),
            pl.col('probabilidade_agravamento').mean().alias('prob_media'),
            (pl.col('probabilidade_agravamento') > 0.7).sum().alias('alto_risco_count')
        ]).sort('prob_media', descending=True).head(10)
        
        especialidades_criticas = df_esp.to_dicts() if len(df_esp) > 0 else []
        
        return {
            'total_sem_agendamento': total,
            'alto_risco_ml': alto_risco,
            'medio_risco_ml': medio_risco,
            'baixo_risco_ml': baixo_risco,
            'agravamento_30_dias': agravamentos_30_dias,
            'agravamento_60_dias': agravamentos_60_dias,
            'agravamento_90_dias': agravamentos_90_dias,
            'custo_estimado_30_dias': custo_30_dias,
            'custo_estimado_total': custo_total,
            'internacoes_projetadas': internacoes,
            'especialidades_criticas_ml': especialidades_criticas,
            'probabilidade_media': df_predicoes['probabilidade_agravamento'].mean(),
            'modelo_metricas': self.metricas
        }

# Instância global do modelo
modelo_global = ModeloPredicaoAgravamento()


