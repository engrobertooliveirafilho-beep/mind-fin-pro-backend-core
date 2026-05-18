class MedicalCurriculumFutureLinker:
    def link(self, subject, topic=""):
        s=(subject or "").lower()
        base={
            "subject":subject,
            "topic":topic,
            "status":"MEDICAL_CURRICULUM_FUTURE_LINK_OPERATIONAL",
            "future_use_cases":[],
            "medical_technologies":[],
            "student_learning_path":[],
            "career_relevance":[],
            "research_angles":[],
            "practical_cases":[]
        }

        if any(x in s for x in ["anatomia","anatomi"]):
            base["future_use_cases"]=["cirurgia","radiologia","ultrassom","exame físico","procedimentos invasivos"]
            base["medical_technologies"]=["cirurgia robótica","realidade aumentada anatômica","IA em imagem médica","modelos 3D","simulação VR"]
            base["student_learning_path"]=["mapear estruturas","associar função","ver em imagem real","aplicar em caso clínico"]
            base["career_relevance"]=["cirurgia","ortopedia","radiologia","emergência","anestesia"]
            base["research_angles"]=["digital twins anatômicos","IA para segmentação de órgãos","treinamento cirúrgico por VR"]
            base["practical_cases"]=["dor abdominal","trauma torácico","AVC","fratura","acesso venoso central"]

        elif any(x in s for x in ["fisiologia","fisiolog"]):
            base["future_use_cases"]=["entender doença","interpretar sinais vitais","suporte intensivo","raciocínio clínico"]
            base["medical_technologies"]=["wearables","monitorização contínua","UTI inteligente","modelos preditivos","digital biomarkers"]
            base["student_learning_path"]=["homeostase","mecanismo","falha fisiológica","tratamento"]
            base["career_relevance"]=["clínica médica","UTI","cardiologia","nefrologia","endocrinologia"]
            base["research_angles"]=["modelagem fisiológica","IA preditiva em UTI","monitoramento remoto"]
            base["practical_cases"]=["choque","insuficiência respiratória","arritmia","acidose","sepse"]

        elif any(x in s for x in ["farmacologia","farmaco"]):
            base["future_use_cases"]=["prescrição segura","interações medicamentosas","dose","terapia personalizada"]
            base["medical_technologies"]=["farmacogenômica","IA para interação medicamentosa","clinical decision support","medicina personalizada"]
            base["student_learning_path"]=["mecanismo","indicação","contraindicação","efeitos adversos","monitoramento"]
            base["career_relevance"]=["todas as áreas clínicas","emergência","UTI","oncologia","psiquiatria"]
            base["research_angles"]=["drug discovery com IA","reposição terapêutica","farmacovigilância"]
            base["practical_cases"]=["antibiótico em sepse","anticoagulação","analgesia","quimioterapia","sedação"]

        elif any(x in s for x in ["patologia","patolog"]):
            base["future_use_cases"]=["diagnóstico diferencial","biópsia","correlação clínica","prognóstico"]
            base["medical_technologies"]=["patologia digital","IA em lâminas histológicas","omics","biomarcadores"]
            base["student_learning_path"]=["lesão celular","inflamação","neoplasia","correlação com exames"]
            base["career_relevance"]=["oncologia","patologia","clínica","cirurgia","radiologia"]
            base["research_angles"]=["IA para histopatologia","biomarcadores prognósticos","medicina molecular"]
            base["practical_cases"]=["câncer","doença autoimune","infarto","inflamação crônica","fibrose"]

        else:
            base["future_use_cases"]=["raciocínio clínico","diagnóstico","prevenção","tratamento","pesquisa médica"]
            base["medical_technologies"]=["IA médica","telemedicina","big data clínico","medicina personalizada","simulação"]
            base["student_learning_path"]=["conceito","mecanismo","caso clínico","tecnologia aplicada","pesquisa"]
            base["career_relevance"]=["clínica","pesquisa","gestão em saúde","educação médica"]
            base["research_angles"]=["avanços globais","novas tecnologias","protocolos comparados"]
            base["practical_cases"]=["caso clínico guiado","discussão diagnóstica","aplicação futura"]

        return base
