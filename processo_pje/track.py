import random
import os
import csv

# Track inspirada na track default do Rally "nested"
# Documentação relevante: 
#  - https://github.com/elastic/rally-tracks/tree/master/nested
#  - https://esrally.readthedocs.io/en/stable/adding_tracks.html#custom-parameter-sources

class QueryParamSource:
    # We need to stick to the param source API
    # noinspection PyUnusedLocal
    def __init__(self, track, params, **kwargs):
        # choose a suitable index: if there is only one defined for this track
        # choose that one, but let the user always override index and type.
        if len(track.indices) == 1:
            default_index = track.indices[0].name
            if len(track.indices[0].types) == 1:
                default_type = track.indices[0].types[0].name
            else:
                default_type = None
        else:
            #default_index = "_all"
            default_index = ','.join(map(str, track.indices))
            default_type = None
        
        # we can eagerly resolve these parameters already in the constructor...
        self._index_name = params.get("index", default_index)
        self._type_name = params.get("type", default_type)
        self._cache = params.get("cache", False)
        self._params = params
        self.infinite = True
        # here we read the queries data file into arrays which we'll then later use randomly.
        self.termos = []
        # be predictably random. The seed has been chosen by a fair dice roll. ;)
        random.seed(4)
        
        # conteudo documento
        cwd = os.path.dirname(__file__)
        with open(os.path.join(cwd, "./data/queries_prd.csv"), "r", encoding="utf-8") as f:
            self.termos = f.readlines()
        
        self.termos = [t.strip() for t in self.termos]

        self.atributos = { 
            "segredo_justica": ["true", "false"],
            "numero_cnj": ["60783072920158130024","61109183520158130024","50011738920158130525","50017426620158130145","50028737220158130114","50004923620168130024","60243589020158130024","60196985320158130024","60223374420158130024","60361556320158130024","60128063120158130024","60145067620148130024","50457320920208130024","50019653520208130471","50003942020208130280","50050985920208130027","50457251720208130024","50002508720208130331","50020231420208130479","50003594420208130738","50002394020208130628","50010245420208130352","50457234720208130024","50036956020208130672","50090843320208130702","50091191920208130079","50007011020208130074","50016889220208130382","50012553320208130271","50001831720208130657","50018470920208130035","50010396420208130209","50018489120208130035","50457191020208130024","50010402320208130153","50005885520208130042","50006579020208130720","50018497620208130035","50006645120208130407","50002343320208130429","50032782020208130313","50007568020208130390","50010259320208130625","50007910220208130241","50011430220208130324","50012561820208130271","50457477520208130024","50049636220208130701","50042997320208130105","50008702520208130194","50013834520208130112","50457303920208130024","50457347620208130024","50090878520208130702","50001564320208130557","50001796720208130240","50001715820208130671","50049653220208130701","50001942820208130081","50009012620208130362","50457373120208130024","50018506120208130035","50002636520208130629","50020416320208130114","50007559520208130390","50001986520208130081","50020228720208130686","50008626420208130512","50002568520208130528","50006397120208130687","50019670520208130471","50091244120208130079","50051002920208130027","50457668120208130024","50008688420208130637","50007029220208130074","50009888720208130521","50003181020208130243","50006524920208130694","50006066120208130144","50051011420208130027","50457364620208130024","50010413420208130209","50002850620208130377","50066681720208130145","50001155520208130273","50050998720208130433","50458386820208130024","50457607420208130024","50012916020208130470","50457486020208130024","50005600420208130005","50091053520208130079","50006963520208130026","50032842720208130313","50003232620208130051","50457624420208130024","50032790520208130313","50019766420208130471","50032093120208130525"]
            }
        
    # We need to stick to the param source API
    # noinspection PyUnusedLocal
    def partition(self, partition_index, total_partitions):
        return self

    # Deprecated - only there for BWC reasons with Rally < 1.4.0
    def size(self):
        return 1


class RadarQuerySimplesTermosRandomicosSource(QueryParamSource):
    def params(self):
        result = {
            "body": {
                "query": {
                    "simple_query_string": {
                        "query": f'%s' % random.choice(self.termos),
                        "fields": [
                            "documentos.conteudo_texto^1.0"
                        ],
                        "flags": -1,
                        "default_operator": "and",
                        "analyze_wildcard": "false",
                        "quote_field_suffix": ".original",
                        "auto_generate_synonyms_phrase_query": "false",
                        "fuzzy_prefix_length": 0,
                        "fuzzy_max_expansions": 50,
                        "fuzzy_transpositions": "false",
                        "boost": 1
                    }
                }
            },
            "index": self._index_name,
            "type": self._type_name,
            "cache": self._cache
        }
        if "cache" in self._params:
            result["cache"] = self._params["cache"]

        return result


class NestedSimpleQueryOnTermVector(QueryParamSource):
    def params(self):
        result = {
            "body": {
                "query":{
                "bool":{
                    "must":[
                        {
                            "bool":{
                            "must":[
                                {
                                    "nested":{
                                        "query":{
                                        "bool":{
                                            "must":[
                                                {
                                                    "simple_query_string":{
                                                    "query": f'%s' % random.choice(self.termos),
                                                    "fields":[
                                                        "documentos.conteudo_texto^1.0"
                                                    ],
                                                    "flags":-1,
                                                    "default_operator":"and",
                                                    "analyze_wildcard":"false",
                                                    "quote_field_suffix":".original",
                                                    "auto_generate_synonyms_phrase_query":"false",
                                                    "fuzzy_prefix_length":0,
                                                    "fuzzy_max_expansions":50,
                                                    "fuzzy_transpositions":"false",
                                                    "boost":1.0
                                                    }
                                                }
                                            ],
                                            "adjust_pure_negative":"true",
                                            "boost":1.0
                                        }
                                        },
                                        "path":"documentos",
                                        "ignore_unmapped":"false",
                                        "score_mode":"none",
                                        "boost":1.0,
                                        "inner_hits":{
                                        "ignore_unmapped":"false",
                                        "from":0,
                                        "size":3,
                                        "version":"false",
                                        "seq_no_primary_term":"false",
                                        "explain":"false",
                                        "track_scores":"false",
                                        "_source":{
                                            "includes":[

                                            ],
                                            "excludes":[
                                                "documentos.conteudo_texto"
                                            ]
                                        },
                                        "highlight":{
                                            "order":"score",
                                            "fields":{
                                                "documentos.conteudo_texto":{
                                                    "pre_tags":[
                                                    "<b>"
                                                    ],
                                                    "post_tags":[
                                                    "</b>"
                                                    ],
                                                    "fragment_size":100,
                                                    "number_of_fragments":5,
                                                    "type":"fvh",
                                                    "fragmenter":"simple",
                                                    "matched_fields":[
                                                    "documentos.conteudo_texto",
                                                    "documentos.conteudo_texto.original"
                                                    ]
                                                }
                                            }
                                        }
                                        }
                                    }
                                }
                            ],
                            "adjust_pure_negative":"true",
                            "boost":1.0
                            }
                        }
                    ],
                    "adjust_pure_negative":"true",
                    "boost":1.0
                }
                },
                "_source":{
                "includes":[

                ],
                "excludes":[
                    "documentos.conteudo_texto"
                ]
                },
                "sort":[
                {
                    "_score":{
                        "order":"desc"
                    }
                }
                ],
                "track_total_hits":2147483647
            },
            "index": self._index_name,
            "type": self._type_name,
            "cache": self._cache
        }
        if "cache" in self._params:
            result["cache"] = self._params["cache"]

        return result


class TermQuery(QueryParamSource):
    def params(self):
        result = {
            "body":{
                "query":{
                    "bool":{
                        "must":[
                            {
                            "bool":{
                                "should":[
                                    {
                                        "bool":{
                                        "must":[
                                            {
                                                "term":{
                                                    self.params["atributo"]:{
                                                    "value": random.choice(self.atributos[self.params["atributo"]]),
                                                    "boost":1.0
                                                    }
                                                }
                                            }
                                        ],
                                        "adjust_pure_negative":"true",
                                        "boost":1.0
                                        }
                                    }
                                ],
                                "adjust_pure_negative":"true",
                                "boost":1.0
                            }
                            }
                        ],
                        "adjust_pure_negative":"true",
                        "boost":1.0
                    }
                },
                "_source":{
                    "includes":[

                    ],
                    "excludes":[
                        "documentos.conteudo_texto"
                    ]
                },
                "sort":[
                    {
                        "_score":{
                            "order":"desc"
                        }
                    }
                ]
            },
            "index": self._index_name,
            "type": self._type_name,
            "cache": self._cache
        }
        if "cache" in self._params:
            result["cache"] = self._params["cache"]

        return result        


class TermsQuery(QueryParamSource):
    def params(self):
        result = {
            "body":{
                "query":{
                    "bool":{
                        "must":[
                            {
                            "bool":{
                                "should":[
                                    {
                                        "bool":{
                                        "should":[
                                            {
                                                "terms":{
                                                    self.params["atributo"] :[random.choice(self.atributos[self.params["atributo"]]) for i in range(5)],
                                                    "boost":1.0
                                                }
                                            }
                                        ],
                                        "adjust_pure_negative":"true",
                                        "boost":1.0
                                        }
                                    }
                                ],
                                "adjust_pure_negative":"true",
                                "boost":1.0
                            }
                            }
                        ],
                        "adjust_pure_negative":"true",
                        "boost":1.0
                    }
                },
                "_source":{
                    "includes":[

                    ],
                    "excludes":[
                        "documentos.conteudo_texto"
                    ]
                },
                "sort":[
                    {
                        "_score":{
                            "order":"desc"
                        }
                    }
                ],
                "track_total_hits":2147483647
            },
            "index": self._index_name,
            "type": self._type_name,
            "cache": self._cache
        }
        if "cache" in self._params:
            result["cache"] = self._params["cache"]

        return result        

def register(registry):
    registry.register_param_source("radar-query-simples-termos-randomicos-source", RadarQuerySimplesTermosRandomicosSource)
    registry.register_param_source("nested-simple-query-in-term-vector-source", NestedSimpleQueryOnTermVector)
    registry.register_param_source("term-query-source", TermQuery)
    registry.register_param_source("terms-query_source", TermsQuery)    