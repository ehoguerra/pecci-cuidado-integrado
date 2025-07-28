#!/usr/bin/env python3
"""
Script para testar a funcionalidade de criptografia das evoluções
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Psicologo, Paciente, Evolucao
from app.utils import encrypt_data, decrypt_data

def test_encryption():
    """Testa a criptografia das evoluções"""
    
    app = create_app()
    
    with app.app_context():
        print("🔐 Testando sistema de criptografia\n")
        
        # Teste básico de criptografia/descriptografia
        texto_original = "Este é um teste de criptografia para evolução de paciente."
        print(f"📝 Texto original: {texto_original}")
        
        # Criptografar
        dados_criptografados = encrypt_data(texto_original)
        if dados_criptografados:
            print(f"🔒 Dados criptografados: {dados_criptografados[:50]}...")
            
            # Descriptografar
            texto_descriptografado = decrypt_data(dados_criptografados)
            print(f"🔓 Texto descriptografado: {texto_descriptografado}")
            
            if texto_original == texto_descriptografado:
                print("✅ Teste de criptografia básica: PASSOU")
            else:
                print("❌ Teste de criptografia básica: FALHOU")
                return False
        else:
            print("❌ Erro na criptografia")
            return False
        
        print("\n" + "="*50)
        
        # Teste com dados reais do banco
        print("🏥 Testando evoluções no banco de dados")
        
        evolucoes = Evolucao.query.all()
        if evolucoes:
            for i, evolucao in enumerate(evolucoes[:2], 1):  # Testar apenas as primeiras 2
                print(f"\n📊 Evolução {i}:")
                print(f"   ID: {evolucao.id}")
                print(f"   Data: {evolucao.data_sessao.strftime('%d/%m/%Y %H:%M')}")
                print(f"   Paciente: {evolucao.paciente.nome_completo}")
                
                # Testar descriptografia
                conteudo_descriptografado = evolucao.conteudo
                if conteudo_descriptografado and not conteudo_descriptografado.startswith("Erro:"):
                    print(f"   Conteúdo (primeiros 100 chars): {conteudo_descriptografado[:100]}...")
                    print("   ✅ Descriptografia: OK")
                else:
                    print(f"   ❌ Erro na descriptografia: {conteudo_descriptografado}")
                    return False
            
            print(f"\n✅ Testadas {min(len(evolucoes), 2)} evoluções com sucesso")
        else:
            print("⚠️  Nenhuma evolução encontrada no banco")
        
        print("\n" + "="*50)
        
        # Teste de criação de nova evolução
        print("➕ Testando criação de nova evolução criptografada")
        
        paciente = Paciente.query.first()
        if paciente:
            from datetime import datetime
            
            nova_evolucao = Evolucao(
                data_sessao=datetime.now(),
                paciente_id=paciente.id
            )
            
            conteudo_teste = "Esta é uma evolução de teste criada automaticamente para verificar a criptografia. O paciente demonstrou progresso significativo na sessão de hoje."
            nova_evolucao.conteudo = conteudo_teste
            
            # Verificar se foi criptografado
            if nova_evolucao.conteudo_criptografado:
                print("   ✅ Conteúdo foi criptografado")
                
                # Verificar se pode ser descriptografado
                conteudo_recuperado = nova_evolucao.conteudo
                if conteudo_recuperado == conteudo_teste:
                    print("   ✅ Conteúdo descriptografado corretamente")
                    
                    # Salvar no banco (mas não fazer commit)
                    db.session.add(nova_evolucao)
                    print("   ✅ Evolução preparada para salvar")
                    
                    # Rollback para não alterar os dados de teste
                    db.session.rollback()
                    print("   ℹ️  Rollback executado (dados de teste preservados)")
                else:
                    print(f"   ❌ Erro na descriptografia: esperado '{conteudo_teste}', obtido '{conteudo_recuperado}'")
                    return False
            else:
                print("   ❌ Falha na criptografia")
                return False
        else:
            print("   ⚠️  Nenhum paciente encontrado para teste")
        
        print("\n🎉 Todos os testes de criptografia passaram!")
        print("\n📋 Resumo:")
        print("   ✅ Criptografia/descriptografia básica")
        print("   ✅ Leitura de evoluções existentes")
        print("   ✅ Criação de nova evolução")
        print("   ✅ Property getters/setters funcionando")
        
        return True

if __name__ == '__main__':
    success = test_encryption()
    if success:
        print("\n🔐 Sistema de criptografia está funcionando perfeitamente!")
        sys.exit(0)
    else:
        print("\n❌ Problemas encontrados no sistema de criptografia!")
        sys.exit(1)
